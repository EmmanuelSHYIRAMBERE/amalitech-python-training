import pytest


@pytest.mark.django_db
def test_health_check_reachable(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Photo Uploader API is healthy"
    assert body["db"] == "reachable"
    assert "timestamp" in body
