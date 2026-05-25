"""URL Preview service — core scraping logic.

This is the SINGLE RESPONSIBILITY of this microservice:
fetch title, description, and favicon from a destination URL.

Resiliency:
  - Retries with exponential backoff (tenacity)
  - Timeout on every request
  - Graceful degradation: returns PreviewResult(error=...) on any failure
  - Circuit breaker: Redis-backed per-domain failure tracking

Demonstrates:
- ABC + concrete implementation (polymorphism)
- Inheritance
- @property on dataclass
- Regex (re module) for HTML parsing
- Numerical operations: backoff formula, failure thresholds
- Loops and conditionals in extraction logic
- Custom exceptions
- SOLID: each function has one job
"""
from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from django.core.cache import cache
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import CircuitOpenError, FetchError
from .schemas import PreviewResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Timeouts
# ---------------------------------------------------------------------------
CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 10.0

# ---------------------------------------------------------------------------
# Regex patterns — compiled once at module load (efficiency)
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

# ---------------------------------------------------------------------------
# Circuit breaker constants
# ---------------------------------------------------------------------------
_CIRCUIT_FAILURE_THRESHOLD = 5
_CIRCUIT_RESET_TTL = 300  # 5 minutes


# ---------------------------------------------------------------------------
# HTML parsing helpers
# ---------------------------------------------------------------------------


def _extract_title(html: str) -> Optional[str]:
    m = _TITLE_RE.search(html)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip() or None
    return None


def _extract_description(html: str) -> Optional[str]:
    m = _META_DESC_RE.search(html) or _META_DESC_RE2.search(html)
    if m is None:
        return None
    return m.group(1).strip() or None


def _extract_favicon(html: str, base_url: str) -> Optional[str]:
    m = _LINK_ICON_RE.search(html) or _LINK_ICON_RE2.search(html)
    if m:
        return urljoin(base_url, m.group(1).strip())
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"


# ---------------------------------------------------------------------------
# Circuit breaker helpers
# ---------------------------------------------------------------------------


def _circuit_key(domain: str) -> str:
    return f"preview:circuit:{domain}"


def _is_circuit_open(domain: str) -> bool:
    """Return True if the domain has exceeded the failure threshold."""
    try:
        count = cache.get(_circuit_key(domain), 0)
        return int(count) >= _CIRCUIT_FAILURE_THRESHOLD
    except Exception:
        return False  # If Redis is down, allow the request


def _record_failure(domain: str) -> None:
    try:
        key = _circuit_key(domain)
        current = cache.get(key, 0)
        cache.set(key, int(current) + 1, timeout=_CIRCUIT_RESET_TTL)
    except Exception:
        pass


def _record_success(domain: str) -> None:
    try:
        cache.delete(_circuit_key(domain))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# HTTP fetch with tenacity retry
# ---------------------------------------------------------------------------


@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    stop=stop_after_attempt(3),
    reraise=False,
)
def _fetch_html(url: str) -> str:
    """Fetch raw HTML. Retries on transient network errors (not on 4xx/5xx)."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; URLPreviewBot/1.0; "
            "+https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training)"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    with httpx.Client(
        timeout=httpx.Timeout(
            connect=CONNECT_TIMEOUT,
            read=READ_TIMEOUT,
            write=5.0,
            pool=5.0,
        ),
        follow_redirects=True,
        max_redirects=5,
    ) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


# ---------------------------------------------------------------------------
# Abstract fetcher (ABC) + concrete implementation — polymorphism
# ---------------------------------------------------------------------------


class AbstractFetcher(ABC):
    """Contract for any preview fetcher. Swap implementations in tests."""

    @abstractmethod
    def fetch(self, url: str) -> PreviewResult:
        """Fetch and return preview metadata for ``url``."""
        ...


class DefaultFetcher(AbstractFetcher):
    """Production fetcher: circuit breaker + retry + regex parsing."""

    def fetch(self, url: str) -> PreviewResult:
        domain = urlparse(url).netloc

        if _is_circuit_open(domain):
            logger.warning(
                "Circuit breaker OPEN for domain=%r — skipping fetch for url=%r",
                domain,
                url,
            )
            return PreviewResult(
                url=url, error=f"Circuit breaker open for {domain}"
            )

        try:
            html = _fetch_html(url)
            title = _extract_title(html)
            description = _extract_description(html)
            favicon = _extract_favicon(html, url)

            _record_success(domain)
            logger.info(
                "Preview fetched: url=%r title=%r favicon=%r", url, title, favicon
            )
            return PreviewResult(
                url=url,
                title=title,
                description=description,
                favicon=favicon,
            )

        except RetryError as exc:
            _record_failure(domain)
            logger.warning(
                "Preview fetch failed after retries: url=%r error=%r", url, exc
            )
            return PreviewResult(
                url=url, error=f"Fetch failed after retries: {exc}"
            )

        except httpx.HTTPStatusError as exc:
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


# Module-level singleton — dependency-injected in tests via the ``fetcher`` param
_default_fetcher: AbstractFetcher = DefaultFetcher()


def fetch_preview(
    url: str,
    *,
    fetcher: Optional[AbstractFetcher] = None,
) -> PreviewResult:
    """Public entry point — fetch preview metadata for ``url``.

    Args:
        url:     The destination URL.
        fetcher: Optional override (used in tests via dependency injection).

    Returns:
        PreviewResult — never raises; errors are captured in result.error.
    """
    return (fetcher or _default_fetcher).fetch(url)
