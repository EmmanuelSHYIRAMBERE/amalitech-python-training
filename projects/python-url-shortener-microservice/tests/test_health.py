"""Tests for core.views — HealthCheckView GET /health/."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient


# ---------------------------------------------------------------------------
# GET /health/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_health_check_returns_200(api_client: APIClient) -> None:
    """GET /health/ must return HTTP 200 OK."""
    response = api_client.get("/health/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_health_check_status_field_is_ok(api_client: APIClient) -> None:
    """Response body must contain {"status": "ok"}."""
    response = api_client.get("/health/")
    assert response.data["status"] == "ok"


@pytest.mark.django_db
def test_health_check_db_field_is_reachable(api_client: APIClient) -> None:
    """Response body must contain {"db": "reachable"} when DB is available."""
    response = api_client.get("/health/")
    assert response.data["db"] == "reachable"


@pytest.mark.django_db
def test_health_check_response_has_exactly_two_fields(api_client: APIClient) -> None:
    """Response body must contain exactly the 'status' and 'db' keys."""
    response = api_client.get("/health/")
    assert set(response.data.keys()) == {"status", "db"}


def test_health_check_returns_500_when_db_unavailable(mocker) -> None:
    """GET /health/ must propagate an exception when the DB connection fails."""
    mocker.patch(
        "core.views.connection.ensure_connection",
        side_effect=Exception("DB unreachable"),
    )
    client = APIClient()
    with pytest.raises(Exception, match="DB unreachable"):
        client.get("/health/")
