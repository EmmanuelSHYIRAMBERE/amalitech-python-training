"""Health check endpoint — no auth required."""

import logging

from django.core.cache import cache
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """GET /health/ — returns 200 when DB + Redis are reachable."""

    permission_classes = [AllowAny]
    throttle_classes: list = []

    def get(self, request: Request) -> Response:
        result: dict[str, str] = {"db": "ok", "redis": "ok", "status": "ok"}
        http_status = 200

        try:
            connection.ensure_connection()
        except Exception as exc:
            logger.error("Health: DB unreachable — %s", exc)
            result.update(db="error", status="degraded")
            http_status = 503

        try:
            cache.set("health_ping", "pong", timeout=5)
            assert cache.get("health_ping") == "pong"
        except Exception as exc:
            logger.error("Health: Redis unreachable — %s", exc)
            result.update(redis="error", status="degraded")
            http_status = 503

        return Response(result, status=http_status)
