"""Shared pytest fixtures for the URL Shortener test suite.

Fixtures defined here are automatically available to every test module
without explicit imports, thanks to pytest's conftest.py discovery.
"""

import pytest
from rest_framework.test import APIClient

from shortener.models import URL


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF APIClient instance for making HTTP requests in tests."""
    return APIClient()


@pytest.fixture
def sample_url_data() -> dict[str, str]:
    """Return a valid payload dict for the POST /api/v1/urls/ endpoint."""
    return {"original_url": "https://www.example.com/some/very/long/path"}


@pytest.fixture
def created_url(db: None) -> URL:
    """Return a persisted URL instance with a known short_code.

    Args:
        db: pytest-django fixture that grants database access.

    Returns:
        A saved URL model instance.
    """
    return URL.objects.create(
        original_url="https://www.example.com/fixture",
        short_code="abc123",
    )
