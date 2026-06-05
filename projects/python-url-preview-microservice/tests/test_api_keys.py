"""Tests for api_keys app — model, authentication, and management endpoints.

Demonstrates:
- pytest fixtures (api_key, auth_client)
- Mocking
- Parametrize for multiple scenarios
- TDD: tests written to express intended behaviour
"""
from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from api_keys.models import APIKey, APIKeyStats, _hash_token


# ---------------------------------------------------------------------------
# APIKey model
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAPIKeyModel:
    def test_create_key_returns_instance_and_raw_token(self):
        key, raw = APIKey.create_key("my-service")
        assert key.pk is not None
        assert key.name == "my-service"
        assert key.is_active is True
        assert len(raw) == 64  # 32 bytes → 64 hex chars

    def test_token_hash_is_not_raw_token(self):
        key, raw = APIKey.create_key("test")
        assert key.token_hash != raw

    def test_token_hash_matches_sha256(self):
        key, raw = APIKey.create_key("test")
        assert key.token_hash == _hash_token(raw)

    def test_authenticate_returns_key_on_valid_token(self):
        key, raw = APIKey.create_key("svc")
        found = APIKey.authenticate(raw)
        assert found is not None
        assert found.pk == key.pk

    def test_authenticate_returns_none_on_invalid_token(self):
        APIKey.create_key("svc")
        assert APIKey.authenticate("wrong-token") is None

    def test_authenticate_increments_request_count(self):
        key, raw = APIKey.create_key("svc")
        APIKey.authenticate(raw)
        key.refresh_from_db()
        assert key.request_count == 1

    def test_authenticate_updates_last_used_at(self):
        key, raw = APIKey.create_key("svc")
        assert key.last_used_at is None
        APIKey.authenticate(raw)
        key.refresh_from_db()
        assert key.last_used_at is not None

    def test_revoke_sets_revoked_at_and_deactivates(self):
        key, raw = APIKey.create_key("svc")
        key.revoke()
        key.refresh_from_db()
        assert key.is_revoked is True
        assert key.is_active is False

    def test_authenticate_returns_none_for_revoked_key(self):
        key, raw = APIKey.create_key("svc")
        key.revoke()
        assert APIKey.authenticate(raw) is None

    def test_is_revoked_false_before_revocation(self):
        key, _ = APIKey.create_key("svc")
        assert key.is_revoked is False

    def test_str_contains_name(self):
        key, _ = APIKey.create_key("my-svc")
        assert "my-svc" in str(key)

    def test_repr_shows_active_status(self):
        key, _ = APIKey.create_key("svc")
        assert "active=True" in repr(key)


# ---------------------------------------------------------------------------
# APIKeyStats dataclass
# ---------------------------------------------------------------------------


class TestAPIKeyStats:
    def test_error_rate_zero_when_no_requests(self):
        from collections import Counter
        stats = APIKeyStats(
            key_id=1,
            key_name="test",
            total_requests=0,
            requests_by_day=Counter(),
            errors_by_type={},
        )
        assert stats.error_rate == 0.0

    def test_error_rate_computed_correctly(self):
        from collections import Counter
        stats = APIKeyStats(
            key_id=1,
            key_name="test",
            total_requests=10,
            requests_by_day=Counter(),
            errors_by_type={"timeout": ["e1", "e2"]},
        )
        assert stats.error_rate == 0.2

    def test_daily_summary_sorted_desc(self):
        from collections import Counter
        stats = APIKeyStats(
            key_id=1,
            key_name="test",
            total_requests=5,
            requests_by_day=Counter({"2026-01-02": 3, "2026-01-01": 2}),
            errors_by_type={},
        )
        summary = stats.daily_summary()
        assert summary[0]["date"] == "2026-01-02"
        assert summary[0]["percentage"] == 60.0


# ---------------------------------------------------------------------------
# Authentication backend
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAPIKeyAuthentication:
    def test_bearer_token_authenticates(self, api_key):
        key, raw = api_key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        response = client.get("/api/v1/preview/health/")
        # Health is AllowAny but confirms no 401
        assert response.status_code == status.HTTP_200_OK

    def test_x_api_key_header_authenticates(self, api_key):
        key, raw = api_key
        client = APIClient()
        client.credentials(HTTP_X_API_KEY=raw)
        response = client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )
        # Not 401 — auth succeeded (may be 200 or mocked)
        assert response.status_code != status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_returns_401(self, db):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token-xyz")
        response = client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_no_token_returns_401(self, db):
        client = APIClient()
        response = client.post(
            "/api/v1/preview/fetch/",
            {"url": "https://example.com"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Key management endpoints
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAPIKeyManagementViews:
    def test_create_key_returns_201_and_token(self, api_client):
        response = api_client.post(
            "/api/v1/keys/",
            {"name": "url-shortener"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert len(response.data["token"]) == 64
        assert response.data["name"] == "url-shortener"

    def test_create_key_missing_name(self, api_client):
        response = api_client.post("/api/v1/keys/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_keys_returns_all(self, db, api_client):
        APIKey.create_key("svc-a")
        APIKey.create_key("svc-b")
        response = api_client.get("/api/v1/keys/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_list_keys_does_not_expose_token(self, db, api_client):
        APIKey.create_key("svc")
        response = api_client.get("/api/v1/keys/")
        for item in response.data:
            assert "token" not in item
            assert "token_hash" not in item

    def test_revoke_key_returns_204(self, db, api_client):
        key, _ = APIKey.create_key("svc")
        response = api_client.delete(f"/api/v1/keys/{key.pk}/revoke/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        key.refresh_from_db()
        assert key.is_active is False

    def test_revoke_nonexistent_key_returns_404(self, db, api_client):
        response = api_client.delete("/api/v1/keys/99999/revoke/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
