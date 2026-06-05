"""Tests for GET /health/ endpoint."""
from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_returns_200(api_client: APIClient) -> None:
    response = api_client.get("/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "ok"


@pytest.mark.django_db
def test_health_contains_db_and_redis_fields(api_client: APIClient) -> None:
    response = api_client.get("/health/")
    assert "db" in response.data
    assert "redis" in response.data


@pytest.mark.django_db
def test_health_no_auth_required(api_client: APIClient) -> None:
    """Health check must be accessible without an API key."""
    response = api_client.get("/health/")
    assert response.status_code != status.HTTP_401_UNAUTHORIZED
