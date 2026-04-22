import logging

from django.db import connection
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    def get(self, request: Request) -> Response:
        connection.ensure_connection()
        logger.debug("Health check passed — DB reachable")
        return Response({"status": "ok", "db": "reachable"})
