"""Views for the URL Preview microservice — Module 9.

Exposes two endpoints:
  POST /api/v1/preview/fetch/   — fetch preview metadata for a given URL
  GET  /api/v1/preview/health/  — liveness check for the preview service

Inter-service communication pattern:
  The shortener app calls POST /api/v1/preview/fetch/ via an HTTP client
  (preview_client.py) rather than importing this module directly.
  This simulates a real microservice boundary.
"""

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

    Accepts a URL and returns scraped metadata from the destination page.
    Authentication required so this endpoint is not abused as an open proxy.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PreviewRequestSerializer,
        responses={200: PreviewResponseSerializer},
        summary="Fetch URL preview metadata (title, description, favicon)",
        description=(
            "Fetches the HTML of the destination URL and extracts "
            "title, meta description, and favicon. "
            "Implements retry with exponential backoff and a per-domain "
            "circuit breaker. Returns partial results on failure."
        ),
    )
    def post(self, request: Request) -> Response:
        serializer = PreviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data["url"]

        logger.info(
            "Preview fetch requested: url=%r user=%r", url, request.user.username
        )
        result = fetch_preview(url)

        return Response(PreviewResponseSerializer(dataclasses.asdict(result)).data)


class PreviewHealthView(APIView):
    """GET /api/v1/preview/health/ — liveness check for the preview service."""

    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, request: Request) -> Response:
        return Response({"status": "ok", "service": "url-preview"})
