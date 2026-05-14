"""Tests for url_preview views — Module 9.

Covers:
  POST /api/v1/preview/fetch/   — authenticated preview fetch
  GET  /api/v1/preview/health/  — public liveness check
"""

from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from url_preview.service import PreviewResult
from users.models import User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _auth_client(user: User) -> APIClient:
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


# ---------------------------------------------------------------------------
# GET /api/v1/preview/health/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_preview_health_returns_200(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/preview/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "ok"
    assert response.data["service"] == "url-preview"


# ---------------------------------------------------------------------------
# POST /api/v1/preview/fetch/ — authentication
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_preview_fetch_requires_authentication(api_client: APIClient) -> None:
    response = api_client.post(
        "/api/v1/preview/fetch/",
        {"url": "https://example.com"},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# POST /api/v1/preview/fetch/ — validation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_preview_fetch_rejects_invalid_url(user: User) -> None:
    client = _auth_client(user)
    response = client.post(
        "/api/v1/preview/fetch/",
        {"url": "not-a-url"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "url" in response.data


@pytest.mark.django_db
def test_preview_fetch_rejects_missing_url(user: User) -> None:
    client = _auth_client(user)
    response = client.post("/api/v1/preview/fetch/", {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# POST /api/v1/preview/fetch/ — happy path
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_preview_fetch_returns_200_with_metadata(user: User) -> None:
    expected = PreviewResult(
        url="https://example.com",
        title="Example Domain",
        description="An example website.",
        favicon="https://example.com/favicon.ico",
    )
    client = _auth_client(user)

    with patch("url_preview.views.fetch_preview", return_value=expected):
        response = client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Example Domain"
    assert response.data["description"] == "An example website."
    assert response.data["favicon"] == "https://example.com/favicon.ico"


@pytest.mark.django_db
def test_preview_fetch_returns_200_with_null_fields_on_failure(user: User) -> None:
    """Graceful degradation: returns 200 with null fields when fetch fails."""
    expected = PreviewResult(
        url="https://example.com",
        error="Circuit breaker open for example.com",
    )
    client = _auth_client(user)

    with patch("url_preview.views.fetch_preview", return_value=expected):
        response = client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] is None
    assert response.data["error"] == "Circuit breaker open for example.com"


@pytest.mark.django_db
def test_preview_fetch_response_contains_expected_fields(user: User) -> None:
    expected = PreviewResult(url="https://example.com", title="T")
    client = _auth_client(user)

    with patch("url_preview.views.fetch_preview", return_value=expected):
        response = client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )

    assert set(response.data.keys()) >= {"url", "title", "description", "favicon"}
