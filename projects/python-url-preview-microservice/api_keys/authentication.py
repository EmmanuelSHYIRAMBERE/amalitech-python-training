"""DRF authentication backend for API key tokens.

Callers pass the token in the Authorization header:
  Authorization: Bearer <token>

or in the X-API-Key header:
  X-API-Key: <token>

Demonstrates:
- Inheritance from BaseAuthentication (OOP)
- @property for type annotation clarity
- Pattern: authenticate() returns (principal, credential) tuple
"""
from __future__ import annotations

import logging
from typing import Optional

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from .models import APIKey

logger = logging.getLogger(__name__)


class APIKeyAuthentication(BaseAuthentication):
    """Authenticate requests using a Bearer token or X-API-Key header."""

    keyword = "Bearer"

    def authenticate(self, request: Request) -> Optional[tuple[APIKey, str]]:
        """Return (api_key, token) or None if no token is present."""
        raw_token = self._extract_token(request)
        if raw_token is None:
            return None  # Let DRF fall through to the next authenticator

        key = APIKey.authenticate(raw_token)
        if key is None:
            logger.warning(
                "Invalid or revoked API key attempt from ip=%r",
                request.META.get("REMOTE_ADDR"),
            )
            raise AuthenticationFailed("Invalid or revoked API key.")

        return key, raw_token

    def authenticate_header(self, request: Request) -> str:
        return self.keyword

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_token(self, request: Request) -> Optional[str]:
        """Try Authorization header first, then X-API-Key header."""
        auth_header: str = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith(f"{self.keyword} "):
            return auth_header[len(self.keyword) + 1:].strip() or None

        x_api_key: str = request.META.get("HTTP_X_API_KEY", "")
        return x_api_key.strip() or None
