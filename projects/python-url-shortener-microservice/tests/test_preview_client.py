"""Tests for shortener.preview_client — Module 9.

Covers:
  - Same-process fallback when PREVIEW_SERVICE_URL is not set
  - HTTP inter-service call happy path
  - Graceful degradation on network failure
  - Graceful degradation on HTTP error response
"""

from unittest.mock import MagicMock, patch

import pytest

from url_preview.service import PreviewResult


# ---------------------------------------------------------------------------
# Same-process fallback (PREVIEW_SERVICE_URL not configured)
# ---------------------------------------------------------------------------


def test_get_url_preview_uses_direct_fallback_when_no_service_url() -> None:
    """When PREVIEW_SERVICE_URL is empty, call fetch_preview directly."""
    expected = PreviewResult(url="https://example.com", title="Direct")

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", ""),
        patch("shortener.preview_client.fetch_preview", return_value=expected) as mock_fetch,
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    mock_fetch.assert_called_once_with("https://example.com")
    assert result.title == "Direct"


# ---------------------------------------------------------------------------
# HTTP inter-service call
# ---------------------------------------------------------------------------


def test_get_url_preview_calls_preview_service_endpoint() -> None:
    """When PREVIEW_SERVICE_URL is set, make an HTTP POST to the service."""
    service_response = {
        "url": "https://example.com",
        "title": "Remote Title",
        "description": "Remote desc",
        "favicon": "https://example.com/fav.ico",
        "error": None,
    }

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch(
            "shortener.preview_client._call_preview_service",
            return_value=service_response,
        ) as mock_call,
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com", access_token="tok123")

    mock_call.assert_called_once_with("https://example.com", "tok123")
    assert result.title == "Remote Title"
    assert result.description == "Remote desc"
    assert result.favicon == "https://example.com/fav.ico"


def test_get_url_preview_degrades_on_network_failure() -> None:
    """Returns a PreviewResult with error when the service is unreachable."""
    from tenacity import RetryError

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch(
            "shortener.preview_client._call_preview_service",
            side_effect=RetryError(MagicMock()),
        ),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    assert result.is_success is False
    assert result.error is not None
    assert "unavailable" in result.error.lower()


def test_get_url_preview_degrades_on_http_error() -> None:
    """Returns a PreviewResult with error on 4xx/5xx from the service."""
    import httpx

    mock_response = MagicMock()
    mock_response.status_code = 503
    exc = httpx.HTTPStatusError("Service Unavailable", request=MagicMock(), response=mock_response)

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client._call_preview_service", side_effect=exc),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    assert result.is_success is False
    assert "503" in result.error  # type: ignore[operator]


def test_get_url_preview_degrades_on_unexpected_error() -> None:
    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch(
            "shortener.preview_client._call_preview_service",
            side_effect=RuntimeError("unexpected"),
        ),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    assert result.is_success is False
    assert result.error is not None
