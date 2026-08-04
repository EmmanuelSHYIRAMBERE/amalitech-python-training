"""Rate throttle scoped to the authenticated API key."""

from __future__ import annotations

from rest_framework.request import Request
from rest_framework.throttling import SimpleRateThrottle


class APIKeyRateThrottle(SimpleRateThrottle):
    """Throttle requests per API key ID (not per IP)."""

    scope = "api_key"

    def get_cache_key(self, request: Request, view) -> str | None:
        from .models import APIKey

        if not isinstance(request.user, APIKey):
            return None  # Unauthenticated — let permission class handle it
        return self.cache_format % {"scope": self.scope, "ident": request.user.pk}
