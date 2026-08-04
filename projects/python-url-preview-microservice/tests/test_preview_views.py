"""Tests for preview views — TDD workflow.

Covers POST /api/v1/preview/fetch/ and GET /api/v1/preview/health/.
Contract is identical to what the url-shortener's test_preview_views.py
validates, so both services stay compatible.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from preview.schemas import PreviewResult


# ---------------------------------------------------------------------------
# GET /api/v1/preview/health/ — no auth
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
# POST /api/v1/preview/fetch/ — input validation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_preview_fetch_rejects_invalid_url(auth_client: APIClient) -> None:
    response = auth_client.post(
        "/api/v1/preview/fetch/",
        {"url": "not-a-url"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "url" in response.data


@pytest.mark.django_db
def test_preview_fetch_rejects_missing_url(auth_client: APIClient) -> None:
    response = auth_client.post("/api/v1/preview/fetch/", {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# POST /api/v1/preview/fetch/ — happy path
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_preview_fetch_returns_200_with_metadata(auth_client: APIClient) -> None:
    expected = PreviewResult(
        url="https://example.com",
        title="Example Domain",
        description="An example website.",
        favicon="https://example.com/favicon.ico",
    )
    with patch("preview.views.fetch_preview", return_value=expected):
        response = auth_client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Example Domain"
    assert response.data["description"] == "An example website."
    assert response.data["favicon"] == "https://example.com/favicon.ico"


@pytest.mark.django_db
def test_preview_fetch_returns_200_with_null_fields_on_failure(
    auth_client: APIClient,
) -> None:
    """Graceful degradation — always 200, error reported in response body."""
    expected = PreviewResult(
        url="https://example.com",
        error="Circuit breaker open for example.com",
    )
    with patch("preview.views.fetch_preview", return_value=expected):
        response = auth_client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] is None
    assert response.data["error"] == "Circuit breaker open for example.com"


@pytest.mark.django_db
def test_preview_fetch_response_contains_expected_fields(
    auth_client: APIClient,
) -> None:
    expected = PreviewResult(url="https://example.com", title="T")
    with patch("preview.views.fetch_preview", return_value=expected):
        response = auth_client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )

    assert set(response.data.keys()) >= {"url", "title", "description", "favicon"}
