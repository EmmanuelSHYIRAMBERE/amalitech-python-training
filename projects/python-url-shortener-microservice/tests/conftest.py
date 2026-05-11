"""Shared pytest fixtures for the URL Shortener test suite — Module 6.

New fixtures:
  user         — a standard free-tier User instance
  premium_user — a premium-tier User instance
  tag_marketing / tag_social — pre-seeded Tag instances
  created_url  — a URL owned by `user` with known short_code
"""

import pytest
from rest_framework.test import APIClient

from shortener.models import URL, Tag
from users.models import User


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF APIClient instance for making HTTP requests in tests."""
    return APIClient()


@pytest.fixture
def sample_url_data() -> dict[str, str]:
    """Return a valid payload dict for the POST /api/v1/urls/ endpoint."""
    return {"original_url": "https://www.example.com/some/very/long/path"}


@pytest.fixture
def user(db: None) -> User:
    """Return a persisted free-tier User."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",
    )


@pytest.fixture
def premium_user(db: None) -> User:
    """Return a persisted premium-tier User."""
    return User.objects.create_user(
        username="premiumuser",
        email="premium@example.com",
        password="testpass123",
        is_premium=True,
        tier=User.Tier.PREMIUM,
    )


@pytest.fixture
def tag_marketing(db: None) -> Tag:
    """Return a persisted Marketing tag."""
    tag, _ = Tag.objects.get_or_create(name="Marketing")
    return tag


@pytest.fixture
def tag_social(db: None) -> Tag:
    """Return a persisted Social tag."""
    tag, _ = Tag.objects.get_or_create(name="Social")
    return tag


@pytest.fixture
def created_url(db: None, user: User) -> URL:
    """Return a persisted URL instance owned by `user` with a known short_code.

    Args:
        db:   pytest-django fixture that grants database access.
        user: the owner User fixture.

    Returns:
        A saved URL model instance.
    """
    return URL.objects.create(
        original_url="https://www.example.com/fixture",
        short_code="abc123",
        owner=user,
    )
