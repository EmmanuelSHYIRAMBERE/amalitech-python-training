"""Tests for preview.service — TDD workflow.

Covers PreviewResult, HTML parsers, circuit breaker, and fetch_preview.
These tests mirror the contract expected by the url-shortener service's
test_preview_service.py so both services stay compatible.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from preview.schemas import PreviewResult
from preview.service import (
    _CIRCUIT_FAILURE_THRESHOLD,
    _circuit_key,
    _extract_description,
    _extract_favicon,
    _extract_title,
    _is_circuit_open,
    _record_failure,
    _record_success,
    fetch_preview,
)


# ---------------------------------------------------------------------------
# PreviewResult value object
# ---------------------------------------------------------------------------


def test_preview_result_is_success_when_title_set() -> None:
    r = PreviewResult(url="https://example.com", title="Hello")
    assert r.is_success is True


def test_preview_result_is_success_when_favicon_set() -> None:
    r = PreviewResult(
        url="https://example.com", favicon="https://example.com/fav.ico"
    )
    assert r.is_success is True


def test_preview_result_not_success_when_all_none() -> None:
    r = PreviewResult(url="https://example.com")
    assert r.is_success is False


def test_preview_result_is_frozen() -> None:
    from dataclasses import FrozenInstanceError

    r = PreviewResult(url="https://example.com", title="T")
    with pytest.raises(FrozenInstanceError):
        r.title = "other"  # type: ignore[misc]


def test_preview_result_metadata_fields_property() -> None:
    r = PreviewResult(url="https://example.com", title="T", description="D")
    fields = r.metadata_fields
    assert fields["title"] == "T"
    assert fields["description"] == "D"
    assert fields["favicon"] is None


# ---------------------------------------------------------------------------
# HTML parsing helpers — parametrized
# ---------------------------------------------------------------------------


def test_extract_title_basic() -> None:
    html = "<html><head><title>My Page</title></head></html>"
    assert _extract_title(html) == "My Page"


def test_extract_title_multiline() -> None:
    html = "<title>\n  Spaced Title\n</title>"
    assert _extract_title(html) == "Spaced Title"


def test_extract_title_missing() -> None:
    assert _extract_title("<html></html>") is None


def test_extract_description_name_first() -> None:
    html = '<meta name="description" content="A great page">'
    assert _extract_description(html) == "A great page"


def test_extract_description_content_first() -> None:
    html = '<meta content="Another desc" name="description">'
    assert _extract_description(html) == "Another desc"


def test_extract_description_missing() -> None:
    assert _extract_description("<html></html>") is None


def test_extract_favicon_from_link_tag() -> None:
    html = '<link rel="icon" href="/favicon.ico">'
    result = _extract_favicon(html, "https://example.com")
    assert result == "https://example.com/favicon.ico"


def test_extract_favicon_absolute_href() -> None:
    html = '<link rel="shortcut icon" href="https://cdn.example.com/fav.png">'
    result = _extract_favicon(html, "https://example.com")
    assert result == "https://cdn.example.com/fav.png"


def test_extract_favicon_fallback_to_root() -> None:
    result = _extract_favicon("<html></html>", "https://example.com/page")
    assert result == "https://example.com/favicon.ico"


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------


def test_circuit_is_closed_by_default() -> None:
    with patch("preview.service.cache") as mock_cache:
        mock_cache.get.return_value = 0
        assert _is_circuit_open("example.com") is False


def test_circuit_opens_at_threshold() -> None:
    with patch("preview.service.cache") as mock_cache:
        mock_cache.get.return_value = _CIRCUIT_FAILURE_THRESHOLD
        assert _is_circuit_open("example.com") is True


def test_record_failure_increments_counter() -> None:
    with patch("preview.service.cache") as mock_cache:
        mock_cache.get.return_value = 2
        mock_cache.set = MagicMock()
        _record_failure("example.com")
        mock_cache.set.assert_called_once()
        args = mock_cache.set.call_args[0]
        assert args[0] == _circuit_key("example.com")
        assert args[1] == 3


def test_record_success_deletes_key() -> None:
    with patch("preview.service.cache") as mock_cache:
        mock_cache.delete = MagicMock()
        _record_success("example.com")
        mock_cache.delete.assert_called_once_with(_circuit_key("example.com"))


def test_circuit_breaker_open_skips_fetch() -> None:
    with patch("preview.service._is_circuit_open", return_value=True):
        result = fetch_preview("https://failing.com/page")
    assert result.is_success is False
    assert result.error is not None
    assert "Circuit breaker" in result.error


# ---------------------------------------------------------------------------
# fetch_preview — happy path
# ---------------------------------------------------------------------------


def test_fetch_preview_returns_title_and_favicon() -> None:
    html = (
        "<html><head>"
        "<title>Example Domain</title>"
        '<meta name="description" content="An example.">'
        '<link rel="icon" href="/fav.ico">'
        "</head></html>"
    )
    with (
        patch("preview.service._is_circuit_open", return_value=False),
        patch("preview.service._fetch_html", return_value=html),
        patch("preview.service._record_success"),
    ):
        result = fetch_preview("https://example.com")

    assert result.title == "Example Domain"
    assert result.description == "An example."
    assert result.favicon == "https://example.com/fav.ico"
    assert result.error is None
    assert result.is_success is True


def test_fetch_preview_records_success_on_hit() -> None:
    html = "<title>T</title>"
    with (
        patch("preview.service._is_circuit_open", return_value=False),
        patch("preview.service._fetch_html", return_value=html),
        patch("preview.service._record_success") as mock_success,
    ):
        fetch_preview("https://example.com")
    mock_success.assert_called_once_with("example.com")


# ---------------------------------------------------------------------------
# fetch_preview — failure modes
# ---------------------------------------------------------------------------


def test_fetch_preview_handles_http_error() -> None:
    import httpx

    mock_response = MagicMock()
    mock_response.status_code = 404
    exc = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with (
        patch("preview.service._is_circuit_open", return_value=False),
        patch("preview.service._fetch_html", side_effect=exc),
        patch("preview.service._record_failure") as mock_fail,
    ):
        result = fetch_preview("https://example.com/missing")

    assert result.is_success is False
    assert "404" in result.error  # type: ignore[operator]
    mock_fail.assert_called_once_with("example.com")


def test_fetch_preview_handles_retry_exhaustion() -> None:
    from tenacity import RetryError

    with (
        patch("preview.service._is_circuit_open", return_value=False),
        patch(
            "preview.service._fetch_html", side_effect=RetryError(MagicMock())
        ),
        patch("preview.service._record_failure") as mock_fail,
    ):
        result = fetch_preview("https://slow.example.com")

    assert result.is_success is False
    assert result.error is not None
    mock_fail.assert_called_once()


def test_fetch_preview_handles_unexpected_exception() -> None:
    with (
        patch("preview.service._is_circuit_open", return_value=False),
        patch("preview.service._fetch_html", side_effect=RuntimeError("boom")),
        patch("preview.service._record_failure") as mock_fail,
    ):
        result = fetch_preview("https://example.com")

    assert result.is_success is False
    assert "boom" in result.error  # type: ignore[operator]
    mock_fail.assert_called_once()
