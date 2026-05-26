"""HTTP client for inter-service communication with the URL Preview service.

The shortener app uses this module to call the preview microservice via HTTP.
The preview microservice runs as a separate service (python-url-preview-microservice)
and is accessed over the network using the configured PREVIEW_SERVICE_URL.

Configuration (via .env):
  PREVIEW_SERVICE_URL  — base URL of the preview microservice
                         e.g. http://preview-service:8001
  PREVIEW_SERVICE_TOKEN — Bearer token for authenticating to the preview service
"""

from __future__ import annotations

import dataclasses
import logging

import httpx
from decouple import config
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


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
        return self.error is None


# Base URL of the preview microservice.
PREVIEW_SERVICE_URL: str = config("PREVIEW_SERVICE_URL", default="")

# Internal service-to-service auth token (optional).
PREVIEW_SERVICE_TOKEN: str = config("PREVIEW_SERVICE_TOKEN", default="")

# Timeout for inter-service HTTP calls.
_TIMEOUT = httpx.Timeout(connect=3.0, read=15.0, write=5.0, pool=5.0)


@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    stop=stop_after_attempt(2),
    reraise=False,
)
def _call_preview_service(url: str, token: str) -> dict[str, str | None]:
    """Make an HTTP POST to the preview microservice endpoint."""
    endpoint = f"{PREVIEW_SERVICE_URL.rstrip('/')}/api/v1/preview/fetch/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    with httpx.Client(timeout=_TIMEOUT) as client:
        response = client.post(endpoint, json={"url": url}, headers=headers)
        response.raise_for_status()
        data: dict[str, str | None] = response.json()
        return data


def get_url_preview(url: str, access_token: str = "") -> PreviewResult:
    """Fetch URL preview metadata via the preview microservice.

    Makes an HTTP POST to the preview microservice endpoint.
    If PREVIEW_SERVICE_URL is not configured, returns a graceful error result
    rather than attempting a local fallback.

    Args:
        url: The destination URL to fetch metadata for.
        access_token: Bearer token to authenticate the inter-service call.

    Returns:
        PreviewResult with title, description, favicon (all nullable).
    """
    token = access_token or PREVIEW_SERVICE_TOKEN

    if not PREVIEW_SERVICE_URL:
        logger.warning("PREVIEW_SERVICE_URL is not configured — skipping preview fetch")
        return PreviewResult(url=url, error="Preview service not configured")

    # Inter-service HTTP call.
    try:
        data = _call_preview_service(url, token)
        logger.info(
            "Preview service response: url=%r title=%r",
            url,
            data.get("title"),
        )
        return PreviewResult(
            url=data.get("url") or url,
            title=data.get("title"),
            description=data.get("description"),
            favicon=data.get("favicon"),
            error=data.get("error"),
        )
    except RetryError as exc:
        logger.warning(
            "Preview service unreachable after retries: url=%r error=%r — degrading gracefully",
            url,
            exc,
        )
        return PreviewResult(url=url, error="Preview service unavailable")
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
