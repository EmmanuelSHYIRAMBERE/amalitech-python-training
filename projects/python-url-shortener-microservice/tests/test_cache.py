"""Tests for shortener.cache — Redis cache utilities.

Tests the cache-aside pattern implementation using mocked cache.
"""

from unittest.mock import MagicMock, patch

import pytest

from shortener.models import URL
from users.models import User


@pytest.mark.django_db
def test_get_cached_url_returns_url_on_cache_miss(user: User) -> None:
    """get_cached_url fetches from DB when cache is empty."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="cach01",
        owner=user,
    )
    with patch("shortener.cache.cache") as mock_cache:
        mock_cache.get.return_value = None  # simulate cache miss
        mock_cache.set = MagicMock()

        from shortener.cache import get_cached_url

        result = get_cached_url("cach01")

    assert result is not None
    assert result.pk == url.pk


@pytest.mark.django_db
def test_get_cached_url_returns_none_for_unknown_code() -> None:
    """get_cached_url returns None for a short_code that doesn't exist."""
    with patch("shortener.cache.cache") as mock_cache:
        mock_cache.get.return_value = None
        mock_cache.set = MagicMock()

        from shortener.cache import get_cached_url

        result = get_cached_url("notexist")

    assert result is None


@pytest.mark.django_db
def test_get_cached_url_uses_cache_on_hit(user: User) -> None:
    """get_cached_url returns URL from cache without hitting the DB."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="cach02",
        owner=user,
    )
    cached_data = {
        "id": url.pk,
        "short_code": "cach02",
        "original_url": "https://example.com",
        "is_active": True,
        "expires_at": None,
    }
    with patch("shortener.cache.cache") as mock_cache:
        mock_cache.get.return_value = cached_data  # simulate cache hit

        from shortener.cache import get_cached_url

        result = get_cached_url("cach02")

    assert result is not None
    assert result.pk == url.pk


@pytest.mark.django_db
def test_invalidate_url_cache_deletes_all_keys(user: User) -> None:
    """invalidate_url_cache deletes all three cache keys for a short_code."""
    URL.objects.create(
        original_url="https://example.com",
        short_code="cach03",
        owner=user,
    )
    with patch("shortener.cache.cache") as mock_cache:
        mock_cache.delete_many = MagicMock()

        from shortener.cache import invalidate_url_cache

        invalidate_url_cache("cach03")

        mock_cache.delete_many.assert_called_once()
        deleted_keys = mock_cache.delete_many.call_args[0][0]
        assert "url:cach03" in deleted_keys
        assert "url:active:cach03" in deleted_keys
        assert "url:expired:cach03" in deleted_keys
