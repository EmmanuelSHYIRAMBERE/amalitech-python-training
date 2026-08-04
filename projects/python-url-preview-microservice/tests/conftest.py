"""Shared pytest fixtures for the URL Preview Microservice test suite.

Demonstrates:
- pytest fixtures (function scope)
- autouse fixtures for isolation
- Factory helpers
"""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from api_keys.models import APIKey


# ---------------------------------------------------------------------------
# Infrastructure isolation
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def disable_throttling(settings):
    """Remove throttle classes so tests are not rate-limited."""
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
    }


@pytest.fixture(autouse=True)
def flush_cache():
    """Clear Redis cache before each test."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


# ---------------------------------------------------------------------------
# HTTP clients
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def api_key(db) -> tuple[APIKey, str]:
    """Return (APIKey instance, raw token)."""
    return APIKey.create_key("test-service")


@pytest.fixture
def auth_client(api_key) -> APIClient:
    """APIClient authenticated with a valid API key."""
    key, raw_token = api_key
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw_token}")
    return client
