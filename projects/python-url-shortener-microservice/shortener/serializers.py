"""DRF serializers for the shortener app — Module 6.

New in Mod 6:
  - TagSerializer          : read-only tag representation.
  - URLCreateSerializer    : accepts tags (by name) and optional custom_alias.
  - URLResponseSerializer  : exposes all new URL fields including tags.
  - ClickSerializer        : read-only analytics row.
  - URLAnalyticsSerializer : aggregated stats per URL (clicks by country).
"""

import logging
from typing import Any

from django.db.models import Count
from rest_framework import serializers
from rest_framework.request import Request

from .generators import default_generator
from .models import Click, Tag, URL
from .protocols import ShortCodeGenerator
from .validators import validate_url_scheme

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

    def validate_original_url(self, value: str) -> str:
        """Enforce http/https scheme using compiled regex."""
        if not validate_url_scheme(value):
            raise serializers.ValidationError(
                "URL must use http:// or https:// scheme."
            )
        return value

    def create(self, validated_data: dict[str, Any]) -> URL:
        # Pop M2M tags before creating the instance — Django requires the
        # instance to exist before M2M relations can be set.
        tags: list[Tag] = validated_data.pop("tags", [])
        short_code = self._generator(length=6)
        url = URL.objects.create(short_code=short_code, **validated_data)
        if tags:
            url.tags.set(tags)
        logger.info(
            "Created short_code=%r for original_url=%r tags=%r",
            url.short_code,
            url.original_url,
            [t.name for t in tags],
        )
        return url


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
        qs = (
            obj.clicks.values("country")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        return list(qs)
