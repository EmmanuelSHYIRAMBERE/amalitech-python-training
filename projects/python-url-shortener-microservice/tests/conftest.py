"""Shared pytest fixtures for the URL Shortener test suite — Module 6 + 7.

New in Mod 7:
  auth_client         — APIClient pre-loaded with a JWT Bearer token for `user`
  premium_auth_client — APIClient pre-loaded with a JWT Bearer token for `premium_user`
"""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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
def auth_client(user: User) -> APIClient:
    """Return an APIClient authenticated as the free-tier `user`."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def premium_auth_client(premium_user: User) -> APIClient:
    """Return an APIClient authenticated as `premium_user`."""
    client = APIClient()
    refresh = RefreshToken.for_user(premium_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


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
