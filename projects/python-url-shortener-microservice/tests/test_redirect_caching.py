"""Tests for RedirectView with Redis caching — Module 8.

Tests the cache-aside pattern in the redirect flow and async task queuing.
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from shortener.models import URL, Click
from users.models import User


@pytest.mark.django_db
def test_redirect_uses_cache_on_hit(user: User) -> None:
    """RedirectView returns 302 using cached URL without DB query."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="redir1",
        owner=user,
    )
    with patch("shortener.views.get_cached_url", return_value=url) as mock_cache, \
         patch("shortener.views.track_click.delay") as mock_task:
        client = APIClient()
        response = client.get("/redir1/")

    assert response.status_code == status.HTTP_302_FOUND
    assert response["Location"] == "https://example.com"
    mock_cache.assert_called_once_with("redir1")


@pytest.mark.django_db
def test_redirect_queues_celery_task(user: User) -> None:
    """RedirectView queues track_click.delay() instead of writing to DB directly."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="redir2",
        owner=user,
    )
    with patch("shortener.views.get_cached_url", return_value=url), \
         patch("shortener.views.track_click.delay") as mock_task:
        client = APIClient()
        client.get("/redir2/", HTTP_USER_AGENT="TestBrowser/1.0")

    # Celery task must be queued with the correct arguments.
    mock_task.assert_called_once()
    call_kwargs = mock_task.call_args.kwargs
    assert call_kwargs["url_id"] == url.pk
    assert call_kwargs["user_agent"] == "TestBrowser/1.0"


@pytest.mark.django_db
def test_redirect_does_not_write_click_synchronously(user: User) -> None:
    """RedirectView must NOT create a Click record in the request/response cycle."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="redir3",
        owner=user,
    )
    with patch("shortener.views.get_cached_url", return_value=url), \
         patch("shortener.views.track_click.delay"):
        client = APIClient()
        client.get("/redir3/")

    # No Click records should exist — they're created by the Celery task.
    assert Click.objects.count() == 0


@pytest.mark.django_db
def test_redirect_inactive_url_returns_404_with_cache(user: User) -> None:
    """RedirectView returns 404 for inactive URLs even when served from cache."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="redir4",
        owner=user,
        is_active=False,
    )
    with patch("shortener.views.get_cached_url", return_value=url), \
         patch("shortener.views.track_click.delay"):
        client = APIClient()
        response = client.get("/redir4/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_redirect_expired_url_returns_404_with_cache(user: User) -> None:
    """RedirectView returns 404 for expired URLs even when served from cache."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="redir5",
        owner=user,
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    with patch("shortener.views.get_cached_url", return_value=url), \
         patch("shortener.views.track_click.delay"):
        client = APIClient()
        response = client.get("/redir5/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_redirect_not_found_returns_404_with_cache() -> None:
    """RedirectView returns 404 when get_cached_url returns None."""
    with patch("shortener.views.get_cached_url", return_value=None):
        client = APIClient()
        response = client.get("/notfound/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
