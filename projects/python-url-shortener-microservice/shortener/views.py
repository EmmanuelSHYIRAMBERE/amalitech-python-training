"""Shortener views — Module 6.

Changes from Mod 5:
  - RedirectView  : uses select_related("owner") to avoid N+1, logs a Click,
                    increments click_count atomically, respects is_active.
  - URLAnalyticsView : returns aggregated click stats for a short code.
"""

import logging

from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ShortLinkExpiredError, ShortLinkInactiveError
from .models import URL, Click
from .serializers import (
    URLAnalyticsSerializer,
    URLCreateSerializer,
    URLResponseSerializer,
)

logger = logging.getLogger(__name__)


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For from proxies."""
    xff: str | None = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return str(request.META.get("REMOTE_ADDR", "0.0.0.0"))


class URLCreateView(APIView):
    @extend_schema(
        request=URLCreateSerializer,
        responses={201: URLResponseSerializer},
        summary="Shorten a URL",
    )
    def post(self, request: Request) -> Response:
        """Create a shortened URL.

        Args:
            request: DRF Request. Body must contain ``original_url``.
                     Optionally accepts ``tags``, ``custom_alias``,
                     ``expires_at``.

        Returns:
            HTTP 201 Created with a URLResponseSerializer payload.

        Raises:
            ValidationError: If ``original_url`` is missing, malformed,
                             or uses a non-http/https scheme.
        """
        serializer = URLCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.save()
        logger.info(
            "POST /api/v1/urls/ — created short_code=%r original_url=%r",
            url.short_code,
            url.original_url,
        )
        return Response(
            URLResponseSerializer(url, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class RedirectView(APIView):
    @extend_schema(exclude=True)
    def get(self, request: Request, short_code: str) -> HttpResponseRedirect:
        """Redirect to the original URL and log the visit.

        Fetches the URL with select_related('owner') to avoid an N+1 query.
        Wraps Click creation and click_count increment in transaction.atomic()
        so both writes succeed or both are rolled back — no partial state.

        Args:
            request: The incoming HTTP request.
            short_code: The short code captured from the URL path.

        Returns:
            HTTP 302 Found redirect to the original URL.

        Raises:
            NotFound: If the short_code does not exist, the link is inactive,
                      or the link has expired.
        """
        url = get_object_or_404(
            URL.objects.select_related("owner"),
            short_code=short_code,
        )

        # Use named exceptions (Clean Code Lab 1 pattern) before converting
        # to DRF NotFound so the reason is explicit in logs and tests.
        try:
            if not url.is_active:
                raise ShortLinkInactiveError(short_code)
            if url.is_expired:
                raise ShortLinkExpiredError(short_code)
        except (ShortLinkInactiveError, ShortLinkExpiredError) as exc:
            logger.warning("Redirect blocked: %s", exc)
            raise NotFound(str(exc)) from exc

        # Wrap both writes in a single transaction — mirrors the ACID
        # transaction pattern from DB Fundamentals Lab 1.
        # If click_count increment fails, the Click row is also rolled back,
        # leaving the DB in a consistent state.
        with transaction.atomic():
            Click.objects.create(
                url=url,
                ip_address=_get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                referrer=request.META.get("HTTP_REFERER") or None,
            )
            url.increment_click_count()

        logger.info(
            "GET /%s/ — redirecting to %r (click_count=%d)",
            short_code,
            url.original_url,
            url.click_count,
        )
        return HttpResponseRedirect(url.original_url)


class URLAnalyticsView(APIView):
    @extend_schema(
        responses={200: URLAnalyticsSerializer},
        summary="Analytics for a short URL",
    )
    def get(self, request: Request, short_code: str) -> Response:
        """Return aggregated click analytics for a short URL.

        Uses prefetch_related('clicks') to load all click records in a
        single extra query, avoiding N+1 when the serializer iterates
        over recent_clicks.

        Args:
            request: The incoming HTTP request.
            short_code: The short code to retrieve analytics for.

        Returns:
            HTTP 200 OK with a URLAnalyticsSerializer payload containing
            click_count, clicks_by_country, and recent_clicks.

        Raises:
            NotFound: If the short_code does not exist.
        """
        url = get_object_or_404(
            URL.objects.prefetch_related("clicks"),
            short_code=short_code,
        )
        return Response(URLAnalyticsSerializer(url).data)
