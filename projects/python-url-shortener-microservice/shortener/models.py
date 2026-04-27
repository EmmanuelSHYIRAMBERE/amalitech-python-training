"""Django models for the shortener app — Module 6.

New in Mod 6:
  - Tag          : M2M categorisation for URLs.
  - URL          : expanded with owner, click_count, is_active, expires_at,
                   title, description, favicon, custom_alias, and tags.
  - Click        : per-visit analytics log (ip, user_agent, country, city, referrer).
  - URLQuerySet  : chainable query helpers (active, expired, popular).
  - URLManager   : attaches URLQuerySet to URL.objects.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.db.models import F
from django.utils import timezone

from core.models import TimeStampedModel

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


class Tag(models.Model):
    """Categorisation label that can be attached to many URLs.

    The M2M relationship lives on URL.tags so Django creates the join table
    automatically (shortener_url_tags).
    """

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        """Developer-friendly representation for debugging and pytest output."""
        return f"Tag(id={self.pk!r}, name={self.name!r})"

    def __eq__(self, other: object) -> bool:
        """Compare tags by name — safe for unsaved instances in tests."""
        if not isinstance(other, Tag):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        """Hash by name so Tag instances work correctly in sets and dict keys."""
        return hash(self.name)


# ---------------------------------------------------------------------------
# URLQuerySet / URLManager
# ---------------------------------------------------------------------------


class URLQuerySet(models.QuerySet["URL"]):
    """Chainable query helpers for the URL model.

    Usage::

        URL.objects.active_urls()
        URL.objects.expired_urls()
        URL.objects.popular_urls(top_n=10)
        URL.objects.active_urls().popular_urls()
    """

    def active_urls(self) -> "URLQuerySet":
        """Return URLs that are active and not yet expired."""
        return self.filter(
            is_active=True,
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        )

    def expired_urls(self) -> "URLQuerySet":
        """Return URLs whose expiry date has passed."""
        return self.filter(
            expires_at__isnull=False,
            expires_at__lte=timezone.now(),
        )

    def popular_urls(self, top_n: int = 10) -> "URLQuerySet":
        """Return the top N URLs ordered by click_count descending."""
        return self.order_by("-click_count")[:top_n]


class URLManager(models.Manager["URL"]):
    """Custom manager that exposes URLQuerySet methods directly on URL.objects."""

    def get_queryset(self) -> URLQuerySet:
        """Return the base URLQuerySet for this manager."""
        return URLQuerySet(self.model, using=self._db)

    def active_urls(self) -> URLQuerySet:
        """Return URLs that are active and not yet expired.

        Returns:
            QuerySet filtered to is_active=True and expires_at in the future
            (or null).
        """
        return self.get_queryset().active_urls()

    def expired_urls(self) -> URLQuerySet:
        """Return URLs whose expiry date has passed.

        Returns:
            QuerySet filtered to expires_at <= now().
        """
        return self.get_queryset().expired_urls()

    def popular_urls(self, top_n: int = 10) -> URLQuerySet:
        """Return the top N URLs ordered by click_count descending.

        Args:
            top_n: Maximum number of results to return. Defaults to 10.

        Returns:
            QuerySet of at most ``top_n`` URLs, ordered by click_count DESC.
        """
        return self.get_queryset().popular_urls(top_n=top_n)


# ---------------------------------------------------------------------------
# URL
# ---------------------------------------------------------------------------


class URL(TimeStampedModel):
    """Maps a short code to an original long URL.

    Module 6 additions over the Mod 5 baseline:
      - owner          : ForeignKey to the custom User model.
      - tags           : M2M to Tag for categorisation.
      - click_count    : denormalised counter for fast read access.
      - is_active      : soft-delete / deactivation flag.
      - expires_at     : optional TTL for the short link.
      - custom_alias   : premium vanity alias (nullable, unique).
      - title          : page title fetched from the destination (Mod 9 preview).
      - description    : meta description from the destination page.
      - favicon        : favicon URL from the destination page.

    Indexes:
      - short_code     : unique B-tree index (fast redirect lookups).
      - created_at     : B-tree index (fast ordering / range queries).
    """

    objects: URLManager = URLManager()

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="urls",
        null=True,  # nullable so Mod 5 tests that create URLs without a user still pass
        blank=True,
    )

    # max_length=2048 covers the practical maximum URL length (RFC 7230).
    original_url = models.URLField(max_length=2048)

    short_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,  # explicit B-tree index for O(log n) redirect lookups
    )

    custom_alias = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Premium vanity alias (e.g. 'my-shop'). Must be unique.",
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="urls",
    )

    click_count = models.PositiveIntegerField(
        default=0,
        help_text="Denormalised counter incremented on every redirect.",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Inactive URLs return 404 on redirect.",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional expiry. Null means the link never expires.",
    )

    # Fields populated by the Mod 9 URL Preview service — nullable here.
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    favicon = models.URLField(max_length=512, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # Explicit composite-friendly index on created_at for range queries.
            models.Index(fields=["created_at"], name="url_created_at_idx"),
            # is_active + expires_at together power active_urls() efficiently.
            models.Index(
                fields=["is_active", "expires_at"], name="url_active_expires_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.short_code} → {self.original_url}"

    def __repr__(self) -> str:
        """Developer-friendly representation for debugging and pytest output."""
        return f"URL(id={self.pk!r}, short_code={self.short_code!r})"

    def __eq__(self, other: object) -> bool:
        """Compare URLs by short_code — safe for unsaved instances in tests."""
        if not isinstance(other, URL):
            return NotImplemented
        # Fall back to pk comparison when both are saved.
        if self.pk is not None and other.pk is not None:
            return self.pk == other.pk
        return self.short_code == other.short_code

    def __hash__(self) -> int:
        """Hash by pk when saved, by short_code when unsaved."""
        if self.pk is not None:
            return hash(self.pk)
        return hash(self.short_code)

    @property
    def is_expired(self) -> bool:
        """Return True if the link has passed its expiry date."""
        return self.expires_at is not None and self.expires_at <= timezone.now()

    def increment_click_count(self) -> None:
        """Atomically increment click_count using F() to avoid race conditions.

        F() translates to SQL: UPDATE shortener_url SET click_count = click_count + 1
        This is safe under concurrent requests — no read-modify-write race.
        """
        URL.objects.filter(pk=self.pk).update(click_count=F("click_count") + 1)
        self.refresh_from_db(fields=["click_count"])
        logger.debug(
            "click_count incremented for short_code=%r → %d",
            self.short_code,
            self.click_count,
        )


# ---------------------------------------------------------------------------
# Click
# ---------------------------------------------------------------------------


class Click(models.Model):
    """Logs every visit to a short link for analytics.

    One row per redirect event. High-volume table — keep it lean.
    Mod 8 will move the write to a Celery background task.
    """

    url = models.ForeignKey(
        URL,
        on_delete=models.CASCADE,
        related_name="clicks",
    )

    clicked_at = models.DateTimeField(auto_now_add=True, db_index=True)

    ip_address = models.GenericIPAddressField(
        protocol="both",  # accepts IPv4 and IPv6
        unpack_ipv4=True,  # stores ::ffff:1.2.3.4 as 1.2.3.4
    )

    user_agent = models.TextField(blank=True, default="")

    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    referrer = models.URLField(
        max_length=2048,
        null=True,
        blank=True,
        help_text="The page the visitor came from (HTTP Referer header).",
    )

    class Meta:
        ordering = ["-clicked_at"]
        indexes = [
            # Power "clicks per country" aggregation queries.
            models.Index(fields=["url", "country"], name="click_url_country_idx"),
            # Power time-series queries (clicks over time).
            models.Index(fields=["url", "clicked_at"], name="click_url_time_idx"),
        ]

    def __str__(self) -> str:
        return f"Click on {self.url.short_code} from {self.ip_address} at {self.clicked_at}"

    def __repr__(self) -> str:
        """Developer-friendly representation for debugging and pytest output."""
        return (
            f"Click(id={self.pk!r}, url_id={self.url_id!r}, "
            f"ip={self.ip_address!r})"
        )
