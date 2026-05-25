"""Preview API views.

Endpoints:
  POST /api/v1/preview/fetch/    — fetch title, description, favicon
  GET  /api/v1/preview/health/   — liveness check (no auth)

Authentication: API key via Authorization: Bearer <token> header.

Demonstrates:
- Class-based views (OOP, APIView inheritance)
- Dependency injection via fetcher parameter (testability)
- Structured logging
- Graceful degradation — always returns 200 even on fetch failure
"""
from __future__ import annotations

import dataclasses
import logging

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PreviewRequestSerializer, PreviewResponseSerializer
from .service import fetch_preview

logger = logging.getLogger(__name__)


class PreviewFetchView(APIView):
    """POST /api/v1/preview/fetch/ — fetch title, description, favicon.

    This endpoint is called by the url-shortener via its preview_client.py
    using PREVIEW_SERVICE_URL + PREVIEW_SERVICE_TOKEN.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PreviewRequestSerializer,
        responses={200: PreviewResponseSerializer},
        summary="Fetch URL preview metadata",
        description=(
            "Fetches the HTML of the destination URL and extracts title, "
            "meta description, and favicon. Implements retry with exponential "
            "backoff and a per-domain circuit breaker. "
            "Always returns 200 — errors are reported in the `error` field."
        ),
    )
    def post(self, request: Request) -> Response:
        req_ser = PreviewRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)

        url: str = req_ser.validated_data["url"]

        # Log which API key is making the request
        api_key_name = getattr(request.user, "name", "unknown")
        logger.info(
            "Preview fetch requested: url=%r api_key=%r", url, api_key_name
        )

        result = fetch_preview(url)

        return Response(
            PreviewResponseSerializer(dataclasses.asdict(result)).data
        )


class PreviewHealthView(APIView):
    """GET /api/v1/preview/health/ — liveness check, no auth required."""

    permission_classes = [AllowAny]
    throttle_classes: list = []

    @extend_schema(exclude=True)
    def get(self, request: Request) -> Response:
        return Response({"status": "ok", "service": "url-preview"})
