"""Cache utilities for the URL Shortener — Module 8.

Implements the cache-aside pattern for URL lookups:
1. Check cache first
2. If miss, fetch from DB and populate cache
3. Invalidate cache on updates/deletes

Cache Keys:
  url:<short_code>           — full URL object (serialized as dict)
  url:active:<short_code>    — boolean is_active flag
  url:expired:<short_code>   — boolean is_expired flag
"""

import logging
from typing import Any

from django.core.cache import cache
from django.utils import timezone

from .models import URL

logger = logging.getLogger(__name__)

# Cache TTLs (in seconds)
URL_CACHE_TTL = 3600  # 1 hour
ACTIVE_FLAG_TTL = 300  # 5 minutes
EXPIRED_FLAG_TTL = 60  # 1 minute (check expiry frequently)


def _url_cache_key(short_code: str) -> str:
    """Return the cache key for a URL object."""
    return f"url:{short_code}"


def _active_cache_key(short_code: str) -> str:
    """Return the cache key for the is_active flag."""
    return f"url:active:{short_code}"


def _expired_cache_key(short_code: str) -> str:
    """Return the cache key for the is_expired flag."""
    return f"url:expired:{short_code}"


def get_cached_url(short_code: str) -> URL | None:
    """Fetch a URL from cache, or from DB if cache miss.

    Args:
        short_code: The short code to look up.

    Returns:
        The URL instance if found, None otherwise.

    Example::

        url = get_cached_url("aB3xYz")
        if url:
            return HttpResponseRedirect(url.original_url)
    """
    cache_key = _url_cache_key(short_code)

    # Try cache first.
    cached_data: dict[str, Any] | None = cache.get(cache_key)
    if cached_data is not None:
        logger.debug("Cache HIT for short_code=%r", short_code)
        # Reconstruct the URL instance from cached dict.
        # We don't cache the full ORM object (not serializable).
        try:
            url = URL.objects.get(pk=cached_data["id"])
            return url
        except URL.DoesNotExist:
            # Stale cache entry — the URL was deleted.
            cache.delete(cache_key)
            logger.warning("Stale cache entry for short_code=%r — deleted", short_code)
            return None

    # Cache miss — fetch from DB.
    logger.debug("Cache MISS for short_code=%r", short_code)
    try:
        url = URL.objects.select_related("owner").get(short_code=short_code)
    except URL.DoesNotExist:
        # Cache the negative result (short_code doesn't exist) to prevent DB hammering.
        cache.set(cache_key, {"id": None}, timeout=60)
        return None

    # Populate cache with a lightweight dict (not the full ORM object).
    cache_data = {
        "id": url.pk,
        "short_code": url.short_code,
        "original_url": url.original_url,
        "is_active": url.is_active,
        "expires_at": url.expires_at.isoformat() if url.expires_at else None,
    }
    cache.set(cache_key, cache_data, timeout=URL_CACHE_TTL)
    logger.info("Cached URL short_code=%r for %d seconds", short_code, URL_CACHE_TTL)
    return url


def is_url_active_cached(short_code: str) -> bool:
    """Check if a URL is active, using cache.

    Args:
        short_code: The short code to check.

    Returns:
        True if active, False otherwise.
    """
    cache_key = _active_cache_key(short_code)
    cached_value = cache.get(cache_key)

    if cached_value is not None:
        return bool(cached_value)

    # Cache miss — fetch from DB.
    try:
        url = URL.objects.only("is_active").get(short_code=short_code)
        cache.set(cache_key, url.is_active, timeout=ACTIVE_FLAG_TTL)
        return url.is_active
    except URL.DoesNotExist:
        cache.set(cache_key, False, timeout=ACTIVE_FLAG_TTL)
        return False


def is_url_expired_cached(short_code: str) -> bool:
    """Check if a URL is expired, using cache.

    Args:
        short_code: The short code to check.

    Returns:
        True if expired, False otherwise.
    """
    cache_key = _expired_cache_key(short_code)
    cached_value = cache.get(cache_key)

    if cached_value is not None:
        return bool(cached_value)

    # Cache miss — fetch from DB.
    try:
        url = URL.objects.only("expires_at").get(short_code=short_code)
        is_expired = url.expires_at is not None and url.expires_at <= timezone.now()
        cache.set(cache_key, is_expired, timeout=EXPIRED_FLAG_TTL)
        return is_expired
    except URL.DoesNotExist:
        cache.set(cache_key, True, timeout=EXPIRED_FLAG_TTL)
        return True


def invalidate_url_cache(short_code: str) -> None:
    """Delete all cache entries for a URL.

    Call this when a URL is updated or deleted.

    Args:
        short_code: The short code whose cache should be invalidated.

    Example::

        # After updating a URL
        url.save()
        invalidate_url_cache(url.short_code)
    """
    keys = [
        _url_cache_key(short_code),
        _active_cache_key(short_code),
        _expired_cache_key(short_code),
    ]
    cache.delete_many(keys)
    logger.info("Invalidated cache for short_code=%r", short_code)


def warm_cache_for_popular_urls(top_n: int = 100) -> None:
    """Pre-populate cache with the most popular URLs.

    This is a maintenance task that can be run periodically (e.g., every hour)
    to ensure hot URLs are always cached.

    Args:
        top_n: Number of top URLs to cache.
    """
    popular_urls = URL.objects.active_urls().popular_urls(top_n=top_n)
    for url in popular_urls:
        cache_data = {
            "id": url.pk,
            "short_code": url.short_code,
            "original_url": url.original_url,
            "is_active": url.is_active,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
        }
        cache.set(_url_cache_key(url.short_code), cache_data, timeout=URL_CACHE_TTL)
    logger.info("Warmed cache for %d popular URLs", len(popular_urls))
