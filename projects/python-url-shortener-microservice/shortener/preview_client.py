"""HTTP client for inter-service communication with the URL Preview service.

The shortener app uses this module to call the preview microservice via HTTP,
simulating a real distributed architecture where services communicate over
the network rather than sharing code directly.

In development / single-container deployments the preview service is hosted
in the same Django process, so the base URL points to localhost.
In a multi-container deployment each service would have its own hostname.

Configuration (via .env):
  PREVIEW_SERVICE_URL  — base URL of the preview service
                         default: http://localhost:8000
  PREVIEW_SERVICE_TOKEN — Bearer token for authenticating to the preview service
                          default: empty (uses the requesting user's token)
"""

from __future__ import annotations

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

from url_preview.service import PreviewResult, fetch_preview

logger = logging.getLogger(__name__)

# Base URL of the preview microservice.
# In a real multi-service deployment this would be a separate hostname.
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
def _call_preview_service(url: str, token: str) -> dict:
    """Make an HTTP POST to the preview microservice endpoint."""
    endpoint = f"{PREVIEW_SERVICE_URL.rstrip('/')}/api/v1/preview/fetch/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    with httpx.Client(timeout=_TIMEOUT) as client:
        response = client.post(endpoint, json={"url": url}, headers=headers)
        response.raise_for_status()
        return response.json()


def get_url_preview(url: str, access_token: str = "") -> PreviewResult:
    """Fetch URL preview metadata via the preview microservice.

    Strategy:
      1. If PREVIEW_SERVICE_URL is configured, call the external HTTP endpoint.
      2. Otherwise, call the service layer function directly (same-process fallback).
         This keeps tests and single-container deployments simple.

    Args:
        url: The destination URL to fetch metadata for.
        access_token: JWT Bearer token to authenticate the inter-service call.

    Returns:
        PreviewResult with title, description, favicon (all nullable).
    """
    token = access_token or PREVIEW_SERVICE_TOKEN

    # Same-process fallback (default for single-container / test environments).
    if not PREVIEW_SERVICE_URL:
        logger.debug("PREVIEW_SERVICE_URL not set — calling service layer directly")
        return fetch_preview(url)

    # Inter-service HTTP call.
    try:
        data = _call_preview_service(url, token)
        logger.info(
            "Preview service response: url=%r title=%r",
            url,
            data.get("title"),
        )
        return PreviewResult(
            url=data.get("url", url),
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
        return PreviewResult(url=url, error=f"Preview service HTTP {exc.response.status_code}")
    except Exception as exc:
        logger.error(
            "Preview service unexpected error: url=%r error=%r",
            url,
            exc,
            exc_info=True,
        )
        return PreviewResult(url=url, error=str(exc))
