"""Core views — health check endpoint."""

import logging

from django.db import connection
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shortener.schemas import HealthResponseDict

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """GET /health/ — verifies the service and DB are reachable."""

    def get(self, request: Request) -> Response:
        connection.ensure_connection()
        logger.debug("Health check passed — DB reachable")
        body: HealthResponseDict = {"status": "ok", "db": "reachable"}
        return Response(body)
