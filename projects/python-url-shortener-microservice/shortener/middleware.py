"""Middleware for structured logging and error tracking — Module 8.

RequestLoggingMiddleware:
  - Logs every request with method, path, status code, and response time
  - Structured JSON format for log aggregation tools (Datadog, ELK, etc.)

custom_exception_handler:
  - DRF exception handler that logs all 500 errors with full context
  - Returns consistent error responses
"""

import logging
import time
from typing import Any

from django.http import HttpRequest, HttpResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Log every HTTP request with structured data.

    Logs include:
      - HTTP method and path
      - Response status code
      - Response time in milliseconds
      - User ID (if authenticated)
      - IP address

    Example log line (JSON format)::

        {
          "timestamp": "2025-01-15T10:30:00Z",
          "level": "INFO",
          "logger": "shortener.middleware",
          "message": "GET /api/v1/urls/ 200 15ms user=42 ip=1.2.3.4"
        }
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Record start time.
        start_time = time.time()

        # Process the request.
        response = self.get_response(request)

        # Calculate response time.
        duration_ms = int((time.time() - start_time) * 1000)

        # Extract user ID if authenticated.
        user_id = getattr(request.user, "pk", None) if hasattr(request, "user") else None

        # Extract client IP.
        ip_address = self._get_client_ip(request)

        # Log the request.
        log_data = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "ip": ip_address,
        }

        # Use different log levels based on status code.
        if response.status_code >= 500:
            logger.error(
                "%s %s %d %dms user=%s ip=%s",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                user_id,
                ip_address,
                extra=log_data,
            )
        elif response.status_code >= 400:
            logger.warning(
                "%s %s %d %dms user=%s ip=%s",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                user_id,
                ip_address,
                extra=log_data,
            )
        else:
            logger.info(
                "%s %s %d %dms user=%s ip=%s",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                user_id,
                ip_address,
                extra=log_data,
            )

        return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract the real client IP, respecting X-Forwarded-For from proxies."""
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Custom DRF exception handler that logs all 500 errors.

    This wraps DRF's default exception_handler and adds structured logging
    for all unhandled exceptions (500 errors).

    Args:
        exc: The exception that was raised.
        context: Dict with 'view' and 'request' keys.

    Returns:
        Response object, or None to fall back to Django's default 500 handler.
    """
    # Call DRF's default handler first to get the standard error response.
    response = exception_handler(exc, context)

    # If response is None, this is an unhandled exception (500 error).
    if response is None:
        request: Request = context.get("request")
        view = context.get("view")

        logger.error(
            "Unhandled exception in %s.%s: %r",
            view.__class__.__module__ if view else "unknown",
            view.__class__.__name__ if view else "unknown",
            exc,
            exc_info=True,
            extra={
                "method": request.method if request else None,
                "path": request.path if request else None,
                "user_id": getattr(request.user, "pk", None)
                if request and hasattr(request, "user")
                else None,
            },
        )

    # If response is not None but status >= 500, log it too.
    elif response.status_code >= 500:
        request: Request = context.get("request")
        logger.error(
            "Server error %d: %r",
            response.status_code,
            exc,
            exc_info=True,
            extra={
                "method": request.method if request else None,
                "path": request.path if request else None,
                "status": response.status_code,
            },
        )

    return response
