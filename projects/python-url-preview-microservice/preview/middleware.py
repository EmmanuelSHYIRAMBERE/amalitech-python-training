"""Request logging middleware and custom exception handler."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("preview")


class RequestLoggingMiddleware:
    """Log every HTTP request with method, path, status, duration, and API key."""

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.monotonic()
        response: HttpResponse = self.get_response(request)
        duration_ms = round((time.monotonic() - start) * 1000)

        ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[
            0
        ].strip() or request.META.get("REMOTE_ADDR", "unknown")

        log_data = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "ip": ip,
        }

        if response.status_code >= 500:
            logger.error("HTTP request", extra=log_data)
        elif response.status_code >= 400:
            logger.warning("HTTP request", extra=log_data)
        else:
            logger.info("HTTP request", extra=log_data)

        return response


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Log unhandled exceptions before delegating to DRF default handler."""
    response = exception_handler(exc, context)
    if response is None:
        request = context.get("request")
        logger.error(
            "Unhandled exception: %s",
            exc,
            extra={
                "method": request.method if request else "?",
                "path": request.path if request else "?",
            },
            exc_info=True,
        )
    return response
