"""Shortener views — Module 6.

Changes from Mod 5:
  - RedirectView  : uses select_related("owner") to avoid N+1, logs a Click,
                    increments click_count atomically, respects is_active.
  - URLAnalyticsView : returns aggregated click stats for a short code.
"""

import logging

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Click, URL
from .serializers import URLAnalyticsSerializer, URLCreateSerializer, URLResponseSerializer

logger = logging.getLogger(__name__)


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For from proxies."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


class URLCreateView(APIView):
    @extend_schema(
        request=URLCreateSerializer,
        responses={201: URLResponseSerializer},
        summary="Shorten a URL",
    )
    def post(self, request: Request) -> Response:
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
        # select_related("owner") fetches the owner in the same SQL JOIN —
        # avoids a second query if owner data is accessed later (N+1 prevention).
        url = get_object_or_404(
            URL.objects.select_related("owner"),
            short_code=short_code,
        )

        # Respect is_active flag — inactive links return 404.
        if not url.is_active or url.is_expired:
            from rest_framework.exceptions import NotFound
            raise NotFound("This short link is no longer active.")

        # Log the click synchronously for now (Mod 8 moves this to Celery).
        Click.objects.create(
            url=url,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referrer=request.META.get("HTTP_REFERER") or None,
        )

        # Atomic increment — safe under concurrent requests.
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
        # prefetch_related("clicks") loads all clicks in a single extra query —
        # avoids N+1 when URLAnalyticsSerializer iterates over recent_clicks.
        url = get_object_or_404(
            URL.objects.prefetch_related("clicks"),
            short_code=short_code,
        )
        return Response(URLAnalyticsSerializer(url).data)
