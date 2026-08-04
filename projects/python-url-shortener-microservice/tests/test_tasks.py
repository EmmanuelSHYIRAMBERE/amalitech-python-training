"""Tests for shortener.tasks — Celery async tasks.

Tests task execution directly (not via the broker) using Django DB access.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from shortener.models import URL, Click
from shortener.tasks import cleanup_expired_urls, track_click
from users.models import User


@pytest.mark.django_db
def test_track_click_creates_click_record(user: User) -> None:
    """track_click creates a Click record in the database."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="task01",
        owner=user,
    )
    result = track_click(
        url_id=url.pk,
        ip_address="1.2.3.4",
        user_agent="TestBrowser/1.0",
        referrer="https://google.com",
    )

    assert result["status"] == "success"
    assert Click.objects.filter(url=url).count() == 1
    click = Click.objects.get(url=url)
    assert click.ip_address == "1.2.3.4"
    assert click.user_agent == "TestBrowser/1.0"
    assert click.referrer == "https://google.com"


@pytest.mark.django_db
def test_track_click_increments_click_count(user: User) -> None:
    """track_click increments the URL's click_count."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="task02",
        owner=user,
        click_count=5,
    )
    track_click(url_id=url.pk, ip_address="1.2.3.4", user_agent="TestBrowser/1.0")

    url.refresh_from_db()
    assert url.click_count == 6


@pytest.mark.django_db
def test_track_click_handles_deleted_url() -> None:
    """track_click returns url_deleted status if URL no longer exists."""
    result = track_click(
        url_id=99999,  # non-existent ID
        ip_address="1.2.3.4",
        user_agent="TestBrowser/1.0",
    )

    assert result["status"] == "url_deleted"


@pytest.mark.django_db
def test_cleanup_expired_urls_deactivates_expired(user: User) -> None:
    """cleanup_expired_urls sets is_active=False on expired URLs."""
    expired = URL.objects.create(
        original_url="https://expired.com",
        short_code="exp001",
        owner=user,
        is_active=True,
        expires_at=timezone.now() - timedelta(hours=1),
    )
    active = URL.objects.create(
        original_url="https://active.com",
        short_code="act001",
        owner=user,
        is_active=True,
        expires_at=timezone.now() + timedelta(hours=1),
    )

    result = cleanup_expired_urls()

    assert result["status"] == "success"
    assert result["deactivated_count"] == 1
    expired.refresh_from_db()
    active.refresh_from_db()
    assert expired.is_active is False
    assert active.is_active is True


@pytest.mark.django_db
def test_cleanup_expired_urls_returns_zero_when_none_expired(user: User) -> None:
    """cleanup_expired_urls returns 0 when no URLs are expired."""
    URL.objects.create(
        original_url="https://active.com",
        short_code="act002",
        owner=user,
        is_active=True,
    )

    result = cleanup_expired_urls()

    assert result["status"] == "success"
    assert result["deactivated_count"] == 0
