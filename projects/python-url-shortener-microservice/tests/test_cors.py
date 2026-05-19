"""Tests for CORS headers — Module 9.

Verifies that the API returns correct CORS headers so a React frontend
can interact with the service from a browser.
"""

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_cors_preflight_returns_200_for_allowed_origin(api_client: APIClient) -> None:
    """OPTIONS preflight from an allowed origin must return 200."""
    response = api_client.options(
        "/api/v1/urls/",
        HTTP_ORIGIN="http://localhost:3000",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
    )
    # django-cors-headers returns 200 for preflight from allowed origins.
    assert response.status_code == 200


@pytest.mark.django_db
def test_cors_header_present_for_allowed_origin(api_client: APIClient) -> None:
    """Responses to requests from allowed origins must include ACAO header."""
    response = api_client.get(
        "/health/",
        HTTP_ORIGIN="http://localhost:3000",
    )
    assert "Access-Control-Allow-Origin" in response


@pytest.mark.django_db
def test_cors_header_value_matches_origin(api_client: APIClient) -> None:
    response = api_client.get(
        "/health/",
        HTTP_ORIGIN="http://localhost:3000",
    )
    assert response["Access-Control-Allow-Origin"] == "http://localhost:3000"


@pytest.mark.django_db
def test_cors_credentials_header_present(api_client: APIClient) -> None:
    """Access-Control-Allow-Credentials must be true for JWT to work."""
    response = api_client.get(
        "/health/",
        HTTP_ORIGIN="http://localhost:3000",
    )
    assert response.get("Access-Control-Allow-Credentials") == "true"
