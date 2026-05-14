"""URL Preview Service — core scraping logic.

Fetches title, description, and favicon from a destination URL using
httpx with retry + exponential backoff. This is the service layer that
the preview microservice endpoint delegates to.

Resiliency:
  - Retries with exponential backoff (tenacity)
  - Timeout on every request (connect + read)
  - Graceful degradation: returns None fields on any failure
  - Circuit breaker: tracks per-domain failure counts in Redis;
    skips fetch if a domain has failed too many times recently.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import httpx
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

CONNECT_TIMEOUT = 5.0   # seconds to establish TCP connection
READ_TIMEOUT    = 10.0  # seconds to read the response body


@dataclass(frozen=True)
class PreviewResult:
    """Immutable result of a URL preview fetch.

    All fields are nullable — a partial result is still useful.
    """

    url: str
    title: str | None = field(default=None)
    description: str | None = field(default=None)
    favicon: str | None = field(default=None)
    error: str | None = field(default=None)

    @property
    def is_success(self) -> bool:
        """Return True if at least one metadata field was populated."""
        return any([self.title, self.description, self.favicon])


# ---------------------------------------------------------------------------
# HTML parsing helpers (no BeautifulSoup dependency — stdlib only)
# ---------------------------------------------------------------------------

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_META_DESC_RE = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
_META_DESC_RE2 = re.compile(
    r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']',
    re.IGNORECASE,
)
_LINK_ICON_RE = re.compile(
    r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
_LINK_ICON_RE2 = re.compile(
    r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*icon[^"\']*["\']',
    re.IGNORECASE,
)


def _extract_title(html: str) -> str | None:
    m = _TITLE_RE.search(html)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip() or None
    return None


def _extract_description(html: str) -> str | None:
    m = _META_DESC_RE.search(html) or _META_DESC_RE2.search(html)
    return m.group(1).strip() or None if m else None


def _extract_favicon(html: str, base_url: str) -> str | None:
    m = _LINK_ICON_RE.search(html) or _LINK_ICON_RE2.search(html)
    if m:
        href = m.group(1).strip()
        # Resolve relative paths against the base URL.
        return urljoin(base_url, href)
    # Fall back to the conventional /favicon.ico path.
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"


# ---------------------------------------------------------------------------
# Circuit breaker (Redis-backed)
# ---------------------------------------------------------------------------

_CIRCUIT_FAILURE_THRESHOLD = 5    # failures before opening the circuit
_CIRCUIT_RESET_TTL         = 300  # seconds before the circuit resets (5 min)


def _circuit_key(domain: str) -> str:
    return f"preview:circuit:{domain}"


def _is_circuit_open(domain: str) -> bool:
    """Return True if the circuit breaker is open for this domain."""
    try:
        from django.core.cache import cache
        count = cache.get(_circuit_key(domain), 0)
        return int(count) >= _CIRCUIT_FAILURE_THRESHOLD
    except Exception:
        return False  # if Redis is down, allow the request


def _record_failure(domain: str) -> None:
    """Increment the failure counter for this domain."""
    try:
        from django.core.cache import cache
        key = _circuit_key(domain)
        current = cache.get(key, 0)
        cache.set(key, int(current) + 1, timeout=_CIRCUIT_RESET_TTL)
    except Exception:
        pass


def _record_success(domain: str) -> None:
    """Reset the failure counter on a successful fetch."""
    try:
        from django.core.cache import cache
        cache.delete(_circuit_key(domain))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# HTTP fetch with retry
# ---------------------------------------------------------------------------

@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    stop=stop_after_attempt(3),
    reraise=False,
)
def _fetch_html(url: str) -> str:
    """Fetch the HTML of a URL with retry on transient network errors.

    Raises:
        httpx.HTTPStatusError: on 4xx/5xx responses (not retried).
        httpx.TimeoutException: on connect/read timeout (retried up to 3x).
        httpx.NetworkError: on DNS/connection failure (retried up to 3x).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; URLShortenerPreviewBot/1.0; "
            "+https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training)"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    with httpx.Client(
        timeout=httpx.Timeout(connect=CONNECT_TIMEOUT, read=READ_TIMEOUT, write=5.0, pool=5.0),
        follow_redirects=True,
        max_redirects=5,
    ) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_preview(url: str) -> PreviewResult:
    """Fetch title, description, and favicon for the given URL.

    This is the main entry point for the preview service layer.
    Implements:
      - Circuit breaker per domain (Redis-backed)
      - Retry with exponential backoff (tenacity)
      - Graceful degradation on any failure

    Args:
        url: The destination URL to fetch metadata for.

    Returns:
        PreviewResult with populated fields on success, error field set on failure.

    Example::

        result = fetch_preview("https://example.com")
        if result.is_success:
            print(result.title)
    """
    domain = urlparse(url).netloc

    # Circuit breaker check — skip fetch if domain is failing repeatedly.
    if _is_circuit_open(domain):
        logger.warning(
            "Circuit breaker OPEN for domain=%r — skipping preview fetch for url=%r",
            domain,
            url,
        )
        return PreviewResult(url=url, error=f"Circuit breaker open for {domain}")

    try:
        html = _fetch_html(url)
        title       = _extract_title(html)
        description = _extract_description(html)
        favicon     = _extract_favicon(html, url)

        _record_success(domain)
        logger.info(
            "Preview fetched: url=%r title=%r favicon=%r",
            url,
            title,
            favicon,
        )
        return PreviewResult(url=url, title=title, description=description, favicon=favicon)

    except RetryError as exc:
        _record_failure(domain)
        logger.warning(
            "Preview fetch failed after retries: url=%r error=%r",
            url,
            exc,
        )
        return PreviewResult(url=url, error=f"Fetch failed after retries: {exc}")

    except httpx.HTTPStatusError as exc:
        # 4xx/5xx — don't retry, but record as a domain failure.
        _record_failure(domain)
        logger.warning(
            "Preview fetch HTTP error: url=%r status=%d",
            url,
            exc.response.status_code,
        )
        return PreviewResult(url=url, error=f"HTTP {exc.response.status_code}")

    except Exception as exc:
        _record_failure(domain)
        logger.error(
            "Preview fetch unexpected error: url=%r error=%r",
            url,
            exc,
            exc_info=True,
        )
        return PreviewResult(url=url, error=str(exc))
