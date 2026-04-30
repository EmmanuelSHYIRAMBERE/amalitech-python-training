"""Shortener views — Module 6 + Module 7.

Module 7 additions:
  - URLCreateView  : requires authentication; passes request to serializer for tier checks.
  - URLListView    : lists the authenticated user's own URLs (paginated).
  - URLDetailView  : retrieve / update / delete with IsOwnerOrReadOnly.
  - URLAnalyticsView : premium-only detailed analytics.
  - RedirectView   : remains public (no auth required for redirects).
"""

import logging

from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ShortLinkExpiredError, ShortLinkInactiveError
from .models import URL, Click
from .permissions import IsOwnerOrReadOnly, IsPremiumUser
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
    """POST /api/v1/urls/ — create a shortened URL.

    Requires authentication.  Tier logic is enforced inside URLCreateSerializer:
      - Free users: max 10 active URLs, no custom_alias.
      - Premium users: unlimited, custom_alias allowed.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=URLCreateSerializer,
        responses={201: URLResponseSerializer},
        summary="Shorten a URL",
    )
    def post(self, request: Request) -> Response:
        serializer = URLCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        url = serializer.save(owner=request.user)
        logger.info(
            "POST /api/v1/urls/ — created short_code=%r original_url=%r user=%r",
            url.short_code,
            url.original_url,
            request.user.username,
        )
        return Response(
            URLResponseSerializer(url, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class URLListView(APIView):
    """GET /api/v1/urls/list/ — list the authenticated user's URLs."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: URLResponseSerializer(many=True)},
        summary="List my shortened URLs",
    )
    def get(self, request: Request) -> Response:
        urls = (
            URL.objects.filter(owner=request.user)
            .prefetch_related("tags")
            .order_by("-created_at")
        )
        serializer = URLResponseSerializer(urls, many=True, context={"request": request})
        return Response(serializer.data)


class URLDetailView(APIView):
    """GET / PUT / DELETE /api/v1/urls/<short_code>/

    - GET    : any authenticated user can read.
    - PUT    : owner only (IsOwnerOrReadOnly).
    - DELETE : owner only (IsOwnerOrReadOnly) — soft-deletes by setting is_active=False.
    """

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def _get_url(self, short_code: str) -> URL:
        return get_object_or_404(
            URL.objects.select_related("owner").prefetch_related("tags"),
            short_code=short_code,
        )

    @extend_schema(responses={200: URLResponseSerializer}, summary="Retrieve a URL")
    def get(self, request: Request, short_code: str) -> Response:
        url = self._get_url(short_code)
        return Response(URLResponseSerializer(url, context={"request": request}).data)

    @extend_schema(
        request=URLCreateSerializer,
        responses={200: URLResponseSerializer},
        summary="Update a URL (owner only)",
    )
    def put(self, request: Request, short_code: str) -> Response:
        url = self._get_url(short_code)
        self.check_object_permissions(request, url)
        serializer = URLCreateSerializer(
            url, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        logger.info("PUT /api/v1/urls/%s/ — updated by user=%r", short_code, request.user.username)
        return Response(URLResponseSerializer(updated, context={"request": request}).data)

    @extend_schema(responses={204: None}, summary="Deactivate a URL (owner only)")
    def delete(self, request: Request, short_code: str) -> Response:
        url = self._get_url(short_code)
        self.check_object_permissions(request, url)
        url.is_active = False
        url.save(update_fields=["is_active", "updated_at"])
        logger.info(
            "DELETE /api/v1/urls/%s/ — deactivated by user=%r", short_code, request.user.username
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RedirectView(APIView):
    """GET /<short_code>/ — public redirect endpoint (no auth required)."""

    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, request: Request, short_code: str) -> HttpResponseRedirect:
        """Redirect to the original URL and log the visit.

        Fetches the URL with select_related('owner') to avoid an N+1 query.
        Wraps Click creation and click_count increment in transaction.atomic().
        """
        url = get_object_or_404(
            URL.objects.select_related("owner"),
            short_code=short_code,
        )

        try:
            if not url.is_active:
                raise ShortLinkInactiveError(short_code)
            if url.is_expired:
                raise ShortLinkExpiredError(short_code)
        except (ShortLinkInactiveError, ShortLinkExpiredError) as exc:
            logger.warning("Redirect blocked: %s", exc)
            raise NotFound(str(exc)) from exc

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
    """GET /api/v1/analytics/<short_code>/ — premium-only detailed analytics."""

    permission_classes = [IsAuthenticated, IsPremiumUser]

    @extend_schema(
        responses={200: URLAnalyticsSerializer},
        summary="Analytics for a short URL (Premium only)",
    )
    def get(self, request: Request, short_code: str) -> Response:
        url = get_object_or_404(
            URL.objects.prefetch_related("clicks"),
            short_code=short_code,
        )
        return Response(URLAnalyticsSerializer(url).data)
