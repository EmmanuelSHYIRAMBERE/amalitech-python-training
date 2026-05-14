"""DRF serializers for the shortener app — Module 6 + Module 7 + Module 9.

New in Mod 9:
  - URLCreateSerializer.create() : queues fetch_url_preview Celery task
    after a URL is saved so title/description/favicon are populated async.
"""

import logging
from datetime import datetime
from typing import Any

from django.db import IntegrityError
from django.db.models import Count
from django.utils import timezone
from rest_framework import serializers
from rest_framework.request import Request

from .exceptions import ShortCodeCollisionError
from .generators import default_generator
from .models import URL, Click, Tag
from .protocols import ShortCodeGenerator
from .validators import validate_url_scheme

FREE_TIER_URL_LIMIT = 10

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


class TagSerializer(serializers.ModelSerializer[Tag]):
    class Meta:
        model = Tag
        fields = ["id", "name"]


# ---------------------------------------------------------------------------
# URL — create
# ---------------------------------------------------------------------------


class URLCreateSerializer(serializers.ModelSerializer[URL]):
    """Serializer for creating a shortened URL.

    Accepts an optional list of tag names (strings).  Tags are looked up
    by name and attached after the URL is saved.

    Args:
        generator: Any object satisfying ``ShortCodeGenerator`` Protocol.
    """

    # Accept tag names as a write-only list of strings.
    # SlugRelatedField maps each string to a Tag instance by its `name` field.
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Tag.objects.all(),
        required=False,
    )

    def __init__(
        self,
        *args: Any,
        generator: ShortCodeGenerator = default_generator,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._generator = generator

    class Meta:
        model = URL
        fields = ["original_url", "custom_alias", "expires_at", "tags"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Enforce tier-based business rules.

        - Free users: max 10 active URLs, no custom_alias.
        - Premium users: unlimited URLs, custom_alias allowed.
        """
        request: Request | None = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            # Custom alias is a premium-only feature.
            if attrs.get("custom_alias") and not user.is_premium:
                raise serializers.ValidationError(
                    {
                        "custom_alias": "Custom aliases are available to Premium users only."
                    }
                )
            # Free tier URL quota.
            if not user.is_premium:
                active_count = URL.objects.filter(owner=user, is_active=True).count()
                if active_count >= FREE_TIER_URL_LIMIT:
                    raise serializers.ValidationError(
                        f"Free users may have at most {FREE_TIER_URL_LIMIT} active URLs. "
                        "Upgrade to Premium for unlimited links."
                    )
        return attrs

    def validate_expires_at(self, value: "datetime | None") -> "datetime | None":
        """Reject expires_at values that are already in the past.

        Args:
            value: The submitted expiry datetime (timezone-aware) or None.

        Returns:
            The validated datetime unchanged, or None.

        Raises:
            ValidationError: If ``value`` is set and is not in the future.
        """
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("expires_at must be a future datetime.")
        return value

    def validate_original_url(self, value: str) -> str:
        """Enforce http/https scheme using compiled regex.

        Django's URLField accepts any scheme (ftp://, ftps://, etc.) by
        design. This validator adds the stricter http/https-only check.

        Args:
            value: The raw URL string submitted by the client.

        Returns:
            The validated URL string, unchanged.

        Raises:
            ValidationError: If the URL does not start with http:// or https://.
        """
        if not validate_url_scheme(value):
            raise serializers.ValidationError(
                "URL must use http:// or https:// scheme."
            )
        return value

    def create(self, validated_data: dict[str, Any]) -> URL:
        """Persist a new URL, retrying on short_code collision.

        Follows the try/except/else/finally pattern from Clean Code Lab 1:
          - except IntegrityError : collision — retry with a new code
          - else                  : success — break the retry loop
          - finally               : always log the attempt for debugging

        Args:
            validated_data: Cleaned data from the serializer fields.

        Returns:
            The newly created URL instance.

        Raises:
            ShortCodeCollisionError: If all retry attempts produce a duplicate
                short_code (extremely unlikely with 62^6 possible codes).
        """
        tags: list[Tag] = validated_data.pop("tags", [])
        _max_attempts = 5
        url: URL | None = None

        for attempt in range(1, _max_attempts + 1):
            short_code = self._generator(length=6)
            try:
                url = URL.objects.create(short_code=short_code, **validated_data)
            except IntegrityError:
                # short_code collision — generate a new one and retry.
                logger.warning(
                    "short_code collision on attempt %d/%d code=%r — retrying",
                    attempt,
                    _max_attempts,
                    short_code,
                )
            else:
                # Success — attach tags and exit the retry loop.
                if tags:
                    url.tags.set(tags)
                logger.info(
                    "Created short_code=%r for original_url=%r tags=%r",
                    url.short_code,
                    url.original_url,
                    [t.name for t in tags],
                )
                break
            finally:
                logger.debug(
                    "create attempt %d/%d short_code=%r",
                    attempt,
                    _max_attempts,
                    short_code,
                )
        else:
            # All attempts exhausted — raise a named application exception.
            raise ShortCodeCollisionError(attempts=_max_attempts)

        assert url is not None  # guaranteed by the else-break above

        # Module 9: Queue async preview enrichment (write-behind).
        # The create response is returned immediately; this task runs in the
        # background and updates title/description/favicon once ready.
        self._queue_preview(url)
        return url

    def _queue_preview(self, url: URL) -> None:
        """Queue the fetch_url_preview Celery task for a newly created URL."""
        try:
            from .tasks import fetch_url_preview
            request: Request | None = self.context.get("request")
            # Forward the access token so the preview service can authenticate.
            token = ""
            if request:
                auth_header: str = request.META.get("HTTP_AUTHORIZATION", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header[len("Bearer "):]
            fetch_url_preview.delay(
                url_id=url.pk,
                original_url=url.original_url,
                access_token=token,
            )
            logger.debug("Queued fetch_url_preview for url_id=%d", url.pk)
        except Exception as exc:  # pragma: no cover
            # Never let a task-queuing failure break the create response.
            logger.warning("Could not queue fetch_url_preview: %r", exc)

    def update(self, instance: URL, validated_data: dict[str, Any]) -> URL:
        """Partial update — used by URLDetailView PUT.

        Tags are re-set when provided; omitting tags leaves them unchanged.
        """
        tags: list[Tag] | None = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        logger.info("Updated URL short_code=%r", instance.short_code)
        return instance


# ---------------------------------------------------------------------------
# URL — response
# ---------------------------------------------------------------------------


class URLResponseSerializer(serializers.ModelSerializer[URL]):
    """Full URL representation returned after create or on detail/list views."""

    short_url = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = URL
        fields = [
            "short_code",
            "original_url",
            "short_url",
            "custom_alias",
            "tags",
            "click_count",
            "is_active",
            "is_expired",
            "expires_at",
            "title",
            "description",
            "favicon",
            "created_at",
        ]

    def get_short_url(self, obj: URL) -> str:
        """Build the absolute short URL for the given URL instance.

        Args:
            obj: The URL model instance being serialized.

        Returns:
            Absolute URI (e.g. ``http://localhost:8000/aB3xYz/``) when a
            request context is available, relative path otherwise.
        """
        request: Request | None = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/{obj.short_code}/")
        return f"/{obj.short_code}/"


# ---------------------------------------------------------------------------
# Click
# ---------------------------------------------------------------------------


class ClickSerializer(serializers.ModelSerializer[Click]):
    """Read-only serializer for a single click/visit record."""

    class Meta:
        model = Click
        fields = [
            "id",
            "clicked_at",
            "ip_address",
            "country",
            "city",
            "user_agent",
            "referrer",
        ]


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class CountryStatSerializer(serializers.Serializer[Any]):
    """One row in the clicks-by-country breakdown."""

    country = serializers.CharField(allow_null=True)
    total = serializers.IntegerField()


class URLAnalyticsSerializer(serializers.ModelSerializer[URL]):
    """Aggregated analytics for a single URL.

    Uses annotate() to compute clicks_by_country directly in the database —
    never in Python — satisfying the Mod 6 aggregation requirement.
    """

    clicks_by_country = serializers.SerializerMethodField()
    recent_clicks = ClickSerializer(many=True, read_only=True, source="clicks")

    class Meta:
        model = URL
        fields = [
            "short_code",
            "original_url",
            "click_count",
            "is_active",
            "expires_at",
            "created_at",
            "clicks_by_country",
            "recent_clicks",
        ]

    def get_clicks_by_country(self, obj: URL) -> list[dict[str, Any]]:
        """Return click totals grouped by country, computed in the DB."""
        qs = obj.clicks.values("country").annotate(total=Count("id")).order_by("-total")
        return list(qs)
