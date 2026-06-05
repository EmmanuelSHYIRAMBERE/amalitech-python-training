"""HTTP client for inter-service communication with the URL Preview service.

The shortener app uses this module to call the preview microservice via HTTP.
The preview microservice runs as a separate service and is accessed over the
network using the configured PREVIEW_SERVICE_URL.

Resiliency stack (outermost → innermost):
  1. Circuit breaker (pybreaker, per domain) — if a domain accumulates
     CIRCUIT_FAIL_MAX consecutive failures its breaker opens and all
     further calls return immediately without touching the network.
     The breaker resets automatically after CIRCUIT_RESET_TIMEOUT seconds.
  2. Retry with exponential backoff (tenacity) — transient network errors
     (timeout, DNS) are retried up to 2 times before the failure is counted
     against the circuit breaker.
  3. Graceful degradation — every code path returns a PreviewResult; this
     function never raises.

Configuration (via .env):
  PREVIEW_SERVICE_URL   — base URL of the preview microservice
                          e.g. http://preview-service:8001
  PREVIEW_SERVICE_TOKEN — Bearer token for authenticating inter-service calls
"""

from __future__ import annotations

import dataclasses
import logging
import os
import threading
from typing import Any
from urllib.parse import urlparse

import httpx
import pybreaker
from decouple import config
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Value object
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class PreviewResult:
    """Metadata returned by the URL preview microservice.

    All fields except ``url`` are nullable — the service may not always be
    able to extract metadata (e.g. the page blocks crawlers, or the network
    call fails).
    """

    url: str
    title: str | None = None
    description: str | None = None
    favicon: str | None = None
    error: str | None = None

    @property
    def is_success(self) -> bool:
        """Return True only when no error was recorded."""
        return self.error is None


# ---------------------------------------------------------------------------
# Module-level configuration
# ---------------------------------------------------------------------------

# Base URL of the preview microservice.
# Read at module load for test/type-checking visibility — get_url_preview
# re-reads via config() at call time so Celery forked workers always use
# the current environment value without requiring a full worker restart.
PREVIEW_SERVICE_URL: str = config("PREVIEW_SERVICE_URL", default="")

# Internal service-to-service auth token (optional).
PREVIEW_SERVICE_TOKEN: str = config("PREVIEW_SERVICE_TOKEN", default="")

# Timeout for inter-service HTTP calls.
_TIMEOUT = httpx.Timeout(connect=3.0, read=15.0, write=5.0, pool=5.0)

# ---------------------------------------------------------------------------
# Circuit breaker configuration
# ---------------------------------------------------------------------------

# How many consecutive failures open the circuit for a domain.
CIRCUIT_FAIL_MAX: int = int(config("CIRCUIT_FAIL_MAX", default="5"))

# Seconds the circuit stays open before moving to half-open and retrying.
CIRCUIT_RESET_TIMEOUT: int = int(config("CIRCUIT_RESET_TIMEOUT", default="60"))


class _PreviewCircuitBreakerListener(pybreaker.CircuitBreakerListener):
    """Logs every circuit breaker state transition for observability."""

    def state_change(self, cb: Any, old_state: Any, new_state: Any) -> None:
        logger.warning(
            "Circuit breaker [%s]: %s → %s (fail_counter=%d)",
            cb.name,
            old_state.name,
            new_state.name,
            cb.fail_counter,
        )

    def failure(self, cb: Any, exc: BaseException) -> None:
        logger.warning(
            "Circuit breaker [%s] failure #%d: %r",
            cb.name,
            cb.fail_counter,
            exc,
        )

    def success(self, cb: pybreaker.CircuitBreaker) -> None:
        logger.debug("Circuit breaker [%s] call succeeded", cb.name)


# Registry of one CircuitBreaker per target domain.
# Guarded by a lock so concurrent Celery workers don't race on creation.
_breakers: dict[str, pybreaker.CircuitBreaker] = {}
_breakers_lock = threading.Lock()


def _get_breaker(domain: str) -> pybreaker.CircuitBreaker:
    """Return the circuit breaker for *domain*, creating it on first use."""
    if domain not in _breakers:
        with _breakers_lock:
            if domain not in _breakers:  # double-checked locking
                _breakers[domain] = pybreaker.CircuitBreaker(
                    fail_max=CIRCUIT_FAIL_MAX,
                    reset_timeout=CIRCUIT_RESET_TIMEOUT,
                    name=domain,
                    listeners=[_PreviewCircuitBreakerListener()],
                )
                logger.debug(
                    "Created circuit breaker for domain=%r "
                    "(fail_max=%d, reset_timeout=%ds)",
                    domain,
                    CIRCUIT_FAIL_MAX,
                    CIRCUIT_RESET_TIMEOUT,
                )
    return _breakers[domain]


# ---------------------------------------------------------------------------
# Low-level HTTP fetch (with tenacity retry)
# ---------------------------------------------------------------------------


@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    stop=stop_after_attempt(2),
    reraise=False,
)
def _call_preview_service(
    url: str, token: str, service_url: str = ""
) -> dict[str, str | None]:
    """POST to /api/v1/preview/fetch/ with retry on transient network errors.

    Retried only for TimeoutException and NetworkError (transient).
    HTTPStatusError (4xx/5xx) is NOT retried — the server explicitly rejected.

    Args:
        url:         Destination URL whose preview metadata to fetch.
        token:       Bearer token for authenticating to the preview service.
        service_url: Base URL of the preview microservice.  Falls back to
                     the module-level PREVIEW_SERVICE_URL when not supplied.

    Raises:
        RetryError: when all retry attempts for transient errors are exhausted.
        httpx.HTTPStatusError: on 4xx/5xx responses.
    """
    base = service_url or PREVIEW_SERVICE_URL
    endpoint = f"{base.rstrip('/')}/api/v1/preview/fetch/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    with httpx.Client(timeout=_TIMEOUT) as client:
        response = client.post(endpoint, json={"url": url}, headers=headers)
        response.raise_for_status()
        data: dict[str, str | None] = response.json()
        return data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_url_preview(
    url: str, access_token: str = ""
) -> PreviewResult:  # noqa: ARG001 (kept for backward compat)
    """Fetch URL preview metadata via the preview microservice.

    Resiliency layers applied (outermost first):
      1. Circuit breaker per domain — open circuit returns immediately.
      2. Tenacity retry — transient network faults are retried ×2.
      3. Graceful degradation — all exception paths return PreviewResult.

    Args:
        url:          The destination URL whose metadata should be fetched.
        access_token: Unused — kept for backward compatibility with callers
                      that forward a user JWT.  The preview microservice uses
                      API key authentication; only PREVIEW_SERVICE_TOKEN is sent.

    Returns:
        PreviewResult — always. Never raises.
    """
    # Re-read from OS environment at call time — Celery ForkPoolWorkers inherit
    # module-level constants AND decouple's internal config cache from the
    # parent process at fork time.  os.environ is never cached, so it always
    # reflects the container's live environment variables regardless of when
    # the worker subprocess was forked.
    #
    # The preview microservice uses API key authentication — always use the
    # static service-to-service token.  The caller-supplied access_token is
    # a user JWT and is intentionally ignored here; it would be rejected by
    # the preview service's APIKeyAuthentication backend.
    token = os.environ.get("PREVIEW_SERVICE_TOKEN", PREVIEW_SERVICE_TOKEN)
    service_url = os.environ.get("PREVIEW_SERVICE_URL", PREVIEW_SERVICE_URL)

    if not service_url:
        logger.warning("PREVIEW_SERVICE_URL is not configured — skipping preview fetch")
        return PreviewResult(url=url, error="Preview service not configured")

    domain = urlparse(url).netloc or url
    breaker = _get_breaker(domain)

    try:
        # The circuit breaker wraps the retrying HTTP call.
        # If the circuit is open pybreaker raises CircuitBreakerError immediately
        # without executing the callable at all.
        data: dict[str, str | None] = breaker.call(
            _call_preview_service, url, token, service_url
        )

        logger.info(
            "Preview fetched: url=%r title=%r domain=%r state=%s",
            url,
            data.get("title"),
            domain,
            breaker.current_state,
        )
        return PreviewResult(
            url=data.get("url") or url,
            title=data.get("title"),
            description=data.get("description"),
            favicon=data.get("favicon"),
            error=data.get("error"),
        )

    except pybreaker.CircuitBreakerError:
        # Circuit is open — domain is failing repeatedly; skip the network call.
        logger.warning(
            "Circuit breaker OPEN for domain=%r — skipping preview fetch for url=%r",
            domain,
            url,
        )
        return PreviewResult(
            url=url,
            error=f"Circuit breaker open for {domain}: too many recent failures",
        )

    except RetryError as exc:
        # All tenacity retries for transient errors exhausted.
        logger.warning(
            "Preview service unreachable after retries: url=%r error=%r — degrading gracefully",
            url,
            exc,
        )
        return PreviewResult(url=url, error="Preview service unavailable after retries")

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Preview service HTTP error: url=%r status=%d",
            url,
            exc.response.status_code,
        )
        return PreviewResult(
            url=url, error=f"Preview service HTTP {exc.response.status_code}"
        )

    except Exception as exc:
        logger.error(
            "Preview service unexpected error: url=%r error=%r",
            url,
            exc,
            exc_info=True,
        )
        return PreviewResult(url=url, error=str(exc))
