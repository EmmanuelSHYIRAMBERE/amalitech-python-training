"""Core views — health check endpoint.

Module 8: Enhanced health check that verifies both PostgreSQL and Redis.
"""

import logging

from django.db import connection
from django_redis import get_redis_connection
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shortener.schemas import HealthResponseDict

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """GET /health/ — verifies the service, DB, and Redis are reachable.

    Returns:
        200 OK if all systems are healthy.
        503 Service Unavailable if any system is down.

    Response body::

        {
          "status": "ok",
          "db": "reachable",
          "redis": "reachable"
        }

    Used by:
      - Load balancers (to route traffic only to healthy instances)
      - Monitoring tools (Datadog, Prometheus, etc.)
      - Docker HEALTHCHECK directive
    """

    permission_classes = [AllowAny]
    throttle_classes: list[type] = []

    def get(self, request: Request) -> Response:
        db_status = "reachable"
        redis_status = "reachable"
        overall_status = "ok"
        http_status = 200

        # Check PostgreSQL.
        try:
            connection.ensure_connection()
            logger.debug("Health check: DB reachable")
        except Exception as exc:
            db_status = f"unreachable: {exc}"
            overall_status = "degraded"
            http_status = 503
            logger.error("Health check: DB unreachable — %r", exc, exc_info=True)

        # Check Redis via a direct PING — bypasses IGNORE_EXCEPTIONS so a silent
        # cache failure doesn't produce a false "unreachable" reading.
        try:
            conn = get_redis_connection("default")
            conn.ping()
            logger.debug("Health check: Redis reachable")
        except Exception as exc:
            redis_status = f"unreachable: {exc}"
            overall_status = "degraded"
            http_status = 503
            logger.error("Health check: Redis unreachable — %r", exc, exc_info=True)

        body: HealthResponseDict = {
            "status": overall_status,
            "db": db_status,
            "redis": redis_status,
        }
        return Response(body, status=http_status)
