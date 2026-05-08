"""Tests for core.views — HealthCheckView GET /health/.

Module 8: Updated to reflect the new redis field in the health response.
"""

from unittest.mock import MagicMock, patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_check_returns_200(api_client: APIClient) -> None:
    """GET /health/ must return HTTP 200 OK when all systems are healthy."""
    with patch("core.views.cache") as mock_cache:
        mock_cache.set = MagicMock()
        mock_cache.get.return_value = "ok"
        response = api_client.get("/health/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_health_check_status_field_is_ok(api_client: APIClient) -> None:
    with patch("core.views.cache") as mock_cache:
        mock_cache.set = MagicMock()
        mock_cache.get.return_value = "ok"
        response = api_client.get("/health/")
    assert response.data["status"] == "ok"


@pytest.mark.django_db
def test_health_check_db_field_is_reachable(api_client: APIClient) -> None:
    with patch("core.views.cache") as mock_cache:
        mock_cache.set = MagicMock()
        mock_cache.get.return_value = "ok"
        response = api_client.get("/health/")
    assert response.data["db"] == "reachable"


@pytest.mark.django_db
def test_health_check_redis_field_is_reachable(api_client: APIClient) -> None:
    with patch("core.views.cache") as mock_cache:
        mock_cache.set = MagicMock()
        mock_cache.get.return_value = "ok"
        response = api_client.get("/health/")
    assert response.data["redis"] == "reachable"


@pytest.mark.django_db
def test_health_check_response_has_exactly_three_fields(api_client: APIClient) -> None:
    with patch("core.views.cache") as mock_cache:
        mock_cache.set = MagicMock()
        mock_cache.get.return_value = "ok"
        response = api_client.get("/health/")
    assert set(response.data.keys()) == {"status", "db", "redis"}


@pytest.mark.django_db
def test_health_check_returns_503_when_db_fails(api_client: APIClient) -> None:
    """GET /health/ returns 503 when the database is unreachable."""
    with patch("core.views.connection.ensure_connection",
               side_effect=Exception("DB unreachable")), \
         patch("core.views.cache") as mock_cache:
        mock_cache.set = MagicMock()
        mock_cache.get.return_value = "ok"
        response = api_client.get("/health/")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.data["status"] == "degraded"


@pytest.mark.django_db
def test_health_check_returns_503_when_redis_fails(api_client: APIClient) -> None:
    """GET /health/ returns 503 when Redis is unreachable."""
    with patch("core.views.cache") as mock_cache:
        mock_cache.set.side_effect = Exception("Redis unreachable")
        response = api_client.get("/health/")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.data["status"] == "degraded"
