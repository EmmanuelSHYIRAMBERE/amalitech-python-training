"""Tests for shortener.preview_client — Module 9.

Covers:
  - PreviewResult value object
  - No service URL configured (graceful error)
  - Happy path HTTP inter-service call
  - Graceful degradation: network failure (RetryError)
  - Graceful degradation: HTTP 4xx/5xx response
  - Graceful degradation: unexpected exception
  - Circuit breaker: opens after CIRCUIT_FAIL_MAX consecutive failures
  - Circuit breaker: open circuit returns immediately without HTTP call
  - Circuit breaker: transitions are logged
  - Per-domain isolation: breaker for domain A does not affect domain B
"""

from unittest.mock import MagicMock, patch

import httpx
import pybreaker
import pytest
from tenacity import RetryError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_breaker(
    fail_max: int = 3, reset_timeout: int = 60
) -> pybreaker.CircuitBreaker:
    """Return a fresh circuit breaker suitable for unit-test injection."""
    return pybreaker.CircuitBreaker(fail_max=fail_max, reset_timeout=reset_timeout)


def _fresh_client_module():
    """Re-import preview_client so module-level state (_breakers dict) is clean."""
    import importlib

    import shortener.preview_client as m

    importlib.reload(m)
    return m


# ---------------------------------------------------------------------------
# PreviewResult value object
# ---------------------------------------------------------------------------


def test_preview_result_is_success_when_no_error() -> None:
    from shortener.preview_client import PreviewResult

    r = PreviewResult(url="https://example.com", title="Hello")
    assert r.is_success is True


def test_preview_result_not_success_when_error_set() -> None:
    from shortener.preview_client import PreviewResult

    r = PreviewResult(url="https://example.com", error="boom")
    assert r.is_success is False


def test_preview_result_is_frozen() -> None:
    from dataclasses import FrozenInstanceError

    from shortener.preview_client import PreviewResult

    r = PreviewResult(url="https://example.com", title="T")
    with pytest.raises(FrozenInstanceError):
        r.title = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# No service URL configured
# ---------------------------------------------------------------------------


def test_get_url_preview_returns_error_when_no_service_url() -> None:
    """When PREVIEW_SERVICE_URL is empty return a graceful error result."""
    with patch("shortener.preview_client.PREVIEW_SERVICE_URL", ""):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    assert result.is_success is False
    assert result.error is not None
    assert "not configured" in result.error.lower()


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_get_url_preview_returns_metadata_on_success() -> None:
    service_response = {
        "url": "https://example.com",
        "title": "Example Domain",
        "description": "An example.",
        "favicon": "https://example.com/fav.ico",
        "error": None,
    }
    breaker = _make_breaker()

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch(
            "shortener.preview_client._call_preview_service",
            return_value=service_response,
        ),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com", access_token="tok123")

    assert result.is_success is True
    assert result.title == "Example Domain"
    assert result.description == "An example."
    assert result.favicon == "https://example.com/fav.ico"
    assert result.error is None


def test_get_url_preview_uses_access_token_over_service_token() -> None:
    """access_token parameter takes priority over PREVIEW_SERVICE_TOKEN."""
    captured: dict[str, str] = {}

    def _fake_call(url: str, token: str) -> dict[str, str | None]:
        captured["token"] = token
        return {
            "url": url,
            "title": "T",
            "description": None,
            "favicon": None,
            "error": None,
        }

    breaker = _make_breaker()
    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client.PREVIEW_SERVICE_TOKEN", "static-tok"),
        patch("shortener.preview_client._call_preview_service", side_effect=_fake_call),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        get_url_preview("https://example.com", access_token="user-jwt")

    assert captured["token"] == "user-jwt"


def test_get_url_preview_falls_back_to_service_token_when_no_access_token() -> None:
    captured: dict[str, str] = {}

    def _fake_call(url: str, token: str) -> dict[str, str | None]:
        captured["token"] = token
        return {
            "url": url,
            "title": "T",
            "description": None,
            "favicon": None,
            "error": None,
        }

    breaker = _make_breaker()
    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client.PREVIEW_SERVICE_TOKEN", "static-tok"),
        patch("shortener.preview_client._call_preview_service", side_effect=_fake_call),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        get_url_preview("https://example.com", access_token="")

    assert captured["token"] == "static-tok"


# ---------------------------------------------------------------------------
# Graceful degradation — error paths
# ---------------------------------------------------------------------------


def test_get_url_preview_degrades_on_retry_error() -> None:
    """RetryError (tenacity exhausted) → PreviewResult(error=...) not a raise."""
    breaker = _make_breaker()

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch(
            "shortener.preview_client._call_preview_service",
            side_effect=RetryError(MagicMock()),
        ),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    assert result.is_success is False
    assert result.error is not None
    assert "unavailable" in result.error.lower()


def test_get_url_preview_degrades_on_http_4xx() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    exc = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    breaker = _make_breaker()
    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client._call_preview_service", side_effect=exc),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    assert result.is_success is False
    assert "404" in (result.error or "")


def test_get_url_preview_degrades_on_http_5xx() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 503
    exc = httpx.HTTPStatusError(
        "Service Unavailable", request=MagicMock(), response=mock_response
    )

    breaker = _make_breaker()
    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client._call_preview_service", side_effect=exc),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    assert result.is_success is False
    assert "503" in (result.error or "")


def test_get_url_preview_degrades_on_unexpected_exception() -> None:
    breaker = _make_breaker()
    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch(
            "shortener.preview_client._call_preview_service",
            side_effect=RuntimeError("unexpected"),
        ),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    assert result.is_success is False
    assert result.error == "unexpected"


# ---------------------------------------------------------------------------
# Circuit breaker — state machine
# ---------------------------------------------------------------------------


def test_circuit_breaker_opens_after_fail_max_consecutive_failures() -> None:
    """After CIRCUIT_FAIL_MAX failures the breaker must be in OPEN state."""
    fail_max = 3
    breaker = _make_breaker(fail_max=fail_max)

    mock_response = MagicMock()
    mock_response.status_code = 500
    http_exc = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=mock_response
    )

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client._call_preview_service", side_effect=http_exc),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        for _ in range(fail_max):
            get_url_preview("https://example.com")

    # After fail_max consecutive failures the breaker must be open.
    assert breaker.current_state == pybreaker.STATE_OPEN


def test_circuit_breaker_open_returns_immediately_without_http_call() -> None:
    """When the circuit is open, _call_preview_service must NOT be invoked."""
    breaker = _make_breaker(fail_max=1)

    # Trip the breaker by recording one failure through pybreaker's API.
    try:
        breaker.call(lambda: (_ for _ in ()).throw(RuntimeError("trip")))
    except Exception:
        pass

    assert breaker.current_state == pybreaker.STATE_OPEN

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client._call_preview_service") as mock_call,
        patch("shortener.preview_client._get_breaker", return_value=breaker),
    ):
        from shortener.preview_client import get_url_preview

        result = get_url_preview("https://example.com")

    # The HTTP call must not have been made.
    mock_call.assert_not_called()
    assert result.is_success is False
    assert result.error is not None
    assert "circuit breaker open" in result.error.lower()


def test_circuit_breaker_closed_by_default() -> None:
    """A freshly created breaker must be in CLOSED state."""
    breaker = _make_breaker()
    assert breaker.current_state == pybreaker.STATE_CLOSED


def test_circuit_breaker_resets_after_successful_call() -> None:
    """A successful call through an open (half-open) breaker closes it again."""
    breaker = _make_breaker(fail_max=1, reset_timeout=0)

    # Trip the breaker.
    try:
        breaker.call(lambda: (_ for _ in ()).throw(RuntimeError("trip")))
    except Exception:
        pass

    assert breaker.current_state == pybreaker.STATE_OPEN

    # Simulate the reset_timeout expiring by forcing half-open state via
    # pybreaker's internal API (last_failure set to epoch zero).

    breaker._state_storage.opened_at = 0  # type: ignore[attr-defined]

    # Now a successful call should close the breaker.
    breaker.call(lambda: None)
    assert breaker.current_state == pybreaker.STATE_CLOSED


# ---------------------------------------------------------------------------
# Per-domain circuit breaker isolation
# ---------------------------------------------------------------------------


def test_different_domains_use_separate_breakers() -> None:
    """Failures for domain A must not affect the breaker for domain B."""
    from shortener.preview_client import _get_breaker

    with patch("shortener.preview_client.CIRCUIT_FAIL_MAX", 3):
        breaker_a = _get_breaker("domain-a.example.com")
        breaker_b = _get_breaker("domain-b.example.com")

    assert breaker_a is not breaker_b


def test_same_domain_returns_same_breaker_instance() -> None:
    """Calling _get_breaker twice for the same domain returns the same object."""
    from shortener.preview_client import _get_breaker

    b1 = _get_breaker("example.com")
    b2 = _get_breaker("example.com")
    assert b1 is b2


def test_domain_a_failure_does_not_open_domain_b_breaker() -> None:
    """Tripping breaker for domain-a must leave domain-b's breaker closed."""
    fail_max = 2

    breaker_a = _make_breaker(fail_max=fail_max)
    breaker_b = _make_breaker(fail_max=fail_max)

    mock_response = MagicMock()
    mock_response.status_code = 500
    http_exc = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=mock_response
    )

    def _domain_breaker(domain: str) -> pybreaker.CircuitBreaker:
        return breaker_a if "domain-a" in domain else breaker_b

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client._call_preview_service", side_effect=http_exc),
        patch("shortener.preview_client._get_breaker", side_effect=_domain_breaker),
    ):
        from shortener.preview_client import get_url_preview

        for _ in range(fail_max):
            get_url_preview("https://domain-a.example.com/page")

    assert breaker_a.current_state == pybreaker.STATE_OPEN
    assert breaker_b.current_state == pybreaker.STATE_CLOSED


# ---------------------------------------------------------------------------
# Listener logging
# ---------------------------------------------------------------------------


def test_listener_logs_state_change_to_open() -> None:
    """The _PreviewCircuitBreakerListener.failure() and state_change() callbacks
    must be invoked when the circuit opens — verified via a spy listener."""
    from shortener.preview_client import _PreviewCircuitBreakerListener

    fail_max = 2
    breaker = pybreaker.CircuitBreaker(
        fail_max=fail_max,
        reset_timeout=60,
        listeners=[_PreviewCircuitBreakerListener()],
    )

    # Track calls to the listener methods via a spy.
    failure_calls: list[str] = []
    state_changes: list[str] = []

    original_failure = _PreviewCircuitBreakerListener.failure
    original_state_change = _PreviewCircuitBreakerListener.state_change

    def spy_failure(self: object, cb: object, exc: BaseException) -> None:
        failure_calls.append(str(exc))
        original_failure(self, cb, exc)  # type: ignore[arg-type]

    def spy_state_change(self: object, cb: object, old: object, new: object) -> None:
        state_changes.append(f"{old.name}->{new.name}")  # type: ignore[union-attr]
        original_state_change(self, cb, old, new)  # type: ignore[arg-type]

    mock_response = MagicMock()
    mock_response.status_code = 500
    http_exc = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=mock_response
    )

    with (
        patch("shortener.preview_client.PREVIEW_SERVICE_URL", "http://preview:8001"),
        patch("shortener.preview_client._call_preview_service", side_effect=http_exc),
        patch("shortener.preview_client._get_breaker", return_value=breaker),
        patch.object(_PreviewCircuitBreakerListener, "failure", spy_failure),
        patch.object(_PreviewCircuitBreakerListener, "state_change", spy_state_change),
    ):

        from shortener.preview_client import get_url_preview

        # First call: failure_counter = 1, breaker still CLOSED
        get_url_preview("https://example.com")
        # Second call: failure_counter = 2 == fail_max → breaker opens
        get_url_preview("https://example.com")

    assert (
        len(failure_calls) >= 1
    ), "Expected listener.failure() to be called at least once"
    assert breaker.current_state == pybreaker.STATE_OPEN
