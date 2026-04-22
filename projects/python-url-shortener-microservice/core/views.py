"""Core views — health check endpoint."""

import logging

from asgiref.sync import sync_to_async
from django.db import connection
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shortener.schemas import HealthResponseDict

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """GET /health/ — verifies the service and DB are reachable.

    Uses ``async def`` + ``sync_to_async`` so the DB connectivity check
    does not block the event loop when running under ASGI (uvicorn).
    Falls back gracefully under WSGI (gunicorn) via Django's sync adapter.
    """

    async def get(self, request: Request) -> Response:
        await sync_to_async(connection.ensure_connection)()
        logger.debug("Health check passed — DB reachable")
        body: HealthResponseDict = {"status": "ok", "db": "reachable"}
        return Response(body)
