"""Celery tasks for the URL Shortener — Module 8 + Module 9.

Module 9 additions:
  - fetch_url_preview: async task that calls the URL Preview service
    after a short URL is created and stores title/description/favicon
    on the URL model.

All tasks are defined here and auto-discovered by Celery via autodiscover_tasks().
"""

import logging
from typing import Any

from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import URL, Click
from .preview_client import get_url_preview

# Module 9 task route is defined in settings.CELERY_TASK_ROUTES.

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=30,
    soft_time_limit=25,
)
def track_click(
    self: Any,
    url_id: int,
    ip_address: str,
    user_agent: str,
    referrer: str | None = None,
    country: str | None = None,
    city: str | None = None,
) -> dict[str, str | int]:
    """Record a click event in the database (write-behind pattern).

    This task is queued by RedirectView instead of writing to the DB synchronously.
    The redirect response is returned immediately, and this task runs in the background.

    Args:
        url_id: Primary key of the URL that was clicked.
        ip_address: Client IP address (IPv4 or IPv6).
        user_agent: Browser/OS string from User-Agent header.
        referrer: HTTP Referer header (where the click came from).
        country: ISO 3166-1 alpha-2 country code (optional, from GeoIP).
        city: City name (optional, from GeoIP).

    Returns:
        Dict with task status and click ID.

    Raises:
        URL.DoesNotExist: If the URL was deleted between redirect and task execution.
        Retry: If the database is temporarily unavailable.
    """
    logger.info(
        "track_click task started: url_id=%d ip=%r user_agent=%r",
        url_id,
        ip_address,
        user_agent[:50],  # truncate long user agents
    )

    try:
        with transaction.atomic():
            # Fetch the URL with select_for_update to prevent race conditions.
            url = URL.objects.select_for_update().get(pk=url_id)

            # Create the Click record.
            click = Click.objects.create(
                url=url,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                country=country,
                city=city,
            )

            # Atomically increment click_count using F() expression.
            URL.objects.filter(pk=url_id).update(click_count=F("click_count") + 1)

        logger.info(
            "track_click task completed: click_id=%d url_id=%d new_count=%d",
            click.pk,
            url_id,
            url.click_count + 1,
        )
        return {"status": "success", "click_id": click.pk, "url_id": url_id}

    except URL.DoesNotExist:
        # The URL was deleted between the redirect and this task execution.
        # This is rare but possible. Don't retry — the URL is gone.
        logger.warning("track_click task failed: URL id=%d no longer exists", url_id)
        return {"status": "url_deleted", "url_id": url_id}

    except Exception as exc:
        # Database connection error, deadlock, etc.
        # Retry with exponential backoff (60s, 120s, 240s).
        logger.error(
            "track_click task failed: url_id=%d error=%r — retrying",
            url_id,
            exc,
            exc_info=True,
        )
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    time_limit=300,
    soft_time_limit=270,
)
def cleanup_expired_urls(self: Any) -> dict[str, str | int]:
    """Archive or deactivate expired URLs (periodic task).

    This task runs nightly via Celery Beat. It finds all URLs whose expires_at
    has passed and sets is_active=False. This prevents expired links from being
    redirected while preserving analytics data.

    Returns:
        Dict with count of deactivated URLs.
    """
    logger.info("cleanup_expired_urls task started")

    now = timezone.now()
    expired_qs = URL.objects.filter(
        is_active=True,
        expires_at__isnull=False,
        expires_at__lte=now,
    )

    count = expired_qs.count()
    if count == 0:
        logger.info("cleanup_expired_urls task completed: no expired URLs found")
        return {"status": "success", "deactivated_count": 0}

    # Bulk update — much faster than iterating and calling save() on each.
    expired_qs.update(is_active=False, updated_at=now)

    logger.info(
        "cleanup_expired_urls task completed: deactivated %d URLs",
        count,
    )
    return {"status": "success", "deactivated_count": count}


@shared_task(
    bind=True,
    time_limit=600,
    soft_time_limit=570,
)
def warm_cache_for_popular_urls(self: Any, top_n: int = 100) -> dict[str, str | int]:
    """Pre-populate cache with the most popular URLs (periodic task).

    This task can run hourly to ensure hot URLs are always cached.

    Args:
        top_n: Number of top URLs to cache.

    Returns:
        Dict with count of cached URLs.
    """
    from .cache import warm_cache_for_popular_urls as warm_cache

    logger.info("warm_cache_for_popular_urls task started: top_n=%d", top_n)
    warm_cache(top_n=top_n)
    logger.info("warm_cache_for_popular_urls task completed")
    return {"status": "success", "cached_count": top_n}


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    time_limit=60,
    soft_time_limit=55,
)
def fetch_url_preview(
    self: Any,
    url_id: int,
    original_url: str,
    access_token: str = "",
) -> dict[str, str | int | None]:
    """Fetch title, description, and favicon for a newly created short URL.

    Module 9 — async preview enrichment (write-behind pattern).

    Called by URLCreateView immediately after a URL is saved. The create
    response is returned to the client right away; this task runs in the
    background and updates the URL record once the preview is ready.

    Args:
        url_id: PK of the URL model instance to enrich.
        original_url: The destination URL to scrape metadata from.
        access_token: JWT token forwarded for inter-service auth.

    Returns:
        Dict with task status and the fetched metadata fields.
    """
    logger.info(
        "fetch_url_preview task started: url_id=%d original_url=%r",
        url_id,
        original_url,
    )

    try:
        if not URL.objects.filter(pk=url_id).exists():
            logger.warning("fetch_url_preview: URL id=%d no longer exists", url_id)
            return {"status": "url_deleted", "url_id": url_id}

        result = get_url_preview(original_url, access_token=access_token)

        # Only update fields that were successfully fetched.
        update_fields: dict[str, str | None] = {}
        if result.title:
            update_fields["title"] = result.title
        if result.description:
            update_fields["description"] = result.description
        if result.favicon:
            update_fields["favicon"] = result.favicon

        if update_fields:
            URL.objects.filter(pk=url_id).update(**update_fields)
            logger.info(
                "fetch_url_preview task completed: url_id=%d fields=%r",
                url_id,
                list(update_fields.keys()),
            )
        else:
            logger.info(
                "fetch_url_preview task: no metadata fetched for url_id=%d error=%r",
                url_id,
                result.error,
            )

        return {
            "status": "success" if update_fields else "no_metadata",
            "url_id": url_id,
            "title": result.title,
            "description": result.description,
            "favicon": result.favicon,
            "error": result.error,
        }

    except Exception as exc:
        logger.error(
            "fetch_url_preview task failed: url_id=%d error=%r — retrying",
            url_id,
            exc,
            exc_info=True,
        )
        raise self.retry(exc=exc)
