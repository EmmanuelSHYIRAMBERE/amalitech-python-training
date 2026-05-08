"""Tests for cache invalidation in URLDetailView — Module 8.

Tests that PUT and DELETE operations invalidate the Redis cache.
"""

from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from shortener.models import URL
from users.models import User


def auth_client(user: User) -> APIClient:
    """Return an APIClient with a valid JWT Bearer token for ``user``."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.mark.django_db
def test_put_invalidates_cache(user: User, created_url: URL) -> None:
    """PUT /api/v1/urls/<code>/ must call invalidate_url_cache."""
    client = auth_client(user)
    with patch("shortener.views.invalidate_url_cache") as mock_invalidate:
        response = client.put(
            f"/api/v1/urls/{created_url.short_code}/",
            {"original_url": "https://updated.com"},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    mock_invalidate.assert_called_once_with(created_url.short_code)


@pytest.mark.django_db
def test_delete_invalidates_cache(user: User, created_url: URL) -> None:
    """DELETE /api/v1/urls/<code>/ must call invalidate_url_cache."""
    client = auth_client(user)
    with patch("shortener.views.invalidate_url_cache") as mock_invalidate:
        response = client.delete(f"/api/v1/urls/{created_url.short_code}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_invalidate.assert_called_once_with(created_url.short_code)
