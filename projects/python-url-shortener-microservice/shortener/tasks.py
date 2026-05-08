"""Celery tasks for the URL Shortener — Module 8.

All tasks are defined here and auto-discovered by Celery via autodiscover_tasks().

Task Naming Convention:
  - Use descriptive names: track_click, cleanup_expired_urls
  - Suffix with _task if ambiguous: send_email_task

Task Best Practices:
  - Keep tasks idempotent (safe to run multiple times)
  - Validate all arguments (never trust queued data)
  - Use explicit timeouts to prevent hanging workers
  - Log task start/end for debugging
"""

import logging
from datetime import datetime

from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import URL, Click

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=30,
    soft_time_limit=25,
)
def track_click(
    self,
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
def cleanup_expired_urls(self) -> dict[str, int]:
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
def warm_cache_for_popular_urls(self, top_n: int = 100) -> dict[str, int]:
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
