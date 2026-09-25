"""Health check -- GET /health (no trailing slash, ALB-compatible)
plus the JSON 404 handler for unmatched routes."""

from __future__ import annotations

from datetime import datetime
from datetime import timezone as dt_timezone

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """GET /health -- DB-connectivity check (upgrade over the Node app's
    static-only response, matching the sibling projects' pattern)."""

    permission_classes = [AllowAny]
    throttle_classes: list = []

    def get(self, request: Request) -> Response:
        db_status = "reachable"
        http_status = 200
        try:
            connection.ensure_connection()
        except Exception:
            db_status = "error"
            http_status = 503

        return Response(
            {
                "success": http_status == 200,
                "message": "Photo Uploader API is healthy",
                "environment": "production" if not settings.DEBUG else "development",
                "timestamp": datetime.now(dt_timezone.utc).isoformat(),
                "db": db_status,
            },
            status=http_status,
        )


def not_found_view(request, exception=None):
    """Django custom 404 handler -- matches Node's catch-all JSON 404 shape
    for any unmatched route (not just /api/v1/*)."""
    return JsonResponse(
        {
            "success": False,
            "statusCode": 404,
            "message": f"Route {request.path} not found",
        },
        status=404,
    )
