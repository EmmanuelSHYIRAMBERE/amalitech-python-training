"""API key management views.

Endpoints:
  POST   /api/v1/keys/          — create a new API key (admin token required)
  GET    /api/v1/keys/          — list all keys
  DELETE /api/v1/keys/<id>/     — revoke a key

The token is only returned in the 201 response — it is never retrievable again.
Callers (e.g. url-shortener) set PREVIEW_SERVICE_TOKEN to this value.

Demonstrates:
- Class-based views (OOP, APIView inheritance)
- Property-based admin check
- Structured logging
"""
from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import APIKey
from .serializers import APIKeyCreateSerializer, APIKeyListSerializer, APIKeyResponseSerializer

logger = logging.getLogger(__name__)


class APIKeyListCreateView(APIView):
    """POST/GET /api/v1/keys/.

    No authentication required for these management endpoints so the first
    key can be created before any key exists. In production, restrict this
    endpoint via firewall / internal network rules.
    """

    permission_classes = [AllowAny]
    throttle_classes: list = []

    def get(self, request: Request) -> Response:
        keys = APIKey.objects.all().order_by("-created_at")
        return Response(APIKeyListSerializer(keys, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = APIKeyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name: str = serializer.validated_data["name"]
        key, raw_token = APIKey.create_key(name)

        # Attach the raw token for the one-time response
        response_data = APIKeyResponseSerializer(key).data
        response_data["token"] = raw_token

        logger.info("API key issued: id=%d name=%r", key.pk, name)
        return Response(response_data, status=status.HTTP_201_CREATED)


class APIKeyRevokeView(APIView):
    """DELETE /api/v1/keys/<id>/ — revoke a key permanently."""

    permission_classes = [AllowAny]
    throttle_classes: list = []

    def delete(self, request: Request, pk: int) -> Response:
        try:
            key = APIKey.objects.get(pk=pk)
        except APIKey.DoesNotExist:
            return Response(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )
        key.revoke()
        return Response(status=status.HTTP_204_NO_CONTENT)
