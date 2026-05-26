"""Shortener views — Module 6 + Module 7 + Module 8.

Module 8 additions:
  - RedirectView     : cache-aside pattern (Redis first, DB fallback).
                       Click tracking moved to Celery task (write-behind).
  - URLDetailView    : cache invalidation on PUT and DELETE.
  - URLCreateView    : unchanged (no caching needed for writes).
  - URLAnalyticsView : unchanged (always fresh data).
"""

import logging

import httpx
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import get_cached_url, invalidate_url_cache
from .exceptions import ShortLinkExpiredError, ShortLinkInactiveError
from .models import URL
from .permissions import IsOwnerOrReadOnly, IsPremiumUser
from .serializers import (
    URLAnalyticsSerializer,
    URLCreateSerializer,
    URLResponseSerializer,
)
from .tasks import track_click

logger = logging.getLogger(__name__)


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For from proxies."""
    xff: str | None = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return str(request.META.get("REMOTE_ADDR", "0.0.0.0"))


_PRIVATE_IP_PREFIXES = ("127.", "10.", "192.168.", "::1", "172.")


def _is_private_ip(ip: str) -> bool:
    return any(ip.startswith(p) for p in _PRIVATE_IP_PREFIXES)


def _lookup_geo(ip: str) -> tuple[str | None, str | None]:
    """Call ip-api.com for the given IP. Returns (country, city) or (None, None)."""
    try:
        resp = httpx.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "country,city,status"},
            timeout=1.5,
        )
        data = resp.json()
        if data.get("status") == "success":
            return data.get("country") or None, data.get("city") or None
    except Exception:
        pass
    return None, None


def _geolocate_ip(ip: str) -> tuple[str | None, str | None]:
    """Return (country, city) for a client IP.

    If the client IP is private (Docker bridge, LAN, loopback) fall back to
    the host's public IP so local development still gets real geo data.
    """
    if not _is_private_ip(ip):
        return _lookup_geo(ip)
    # Private IP — try to resolve the host machine's public IP instead.
    try:
        resp = httpx.get(
            "http://ip-api.com/json/",
            params={"fields": "country,city,status,query"},
            timeout=1.5,
        )
        data = resp.json()
        if data.get("status") == "success":
            return data.get("country") or None, data.get("city") or None
    except Exception:
        pass
    return None, None


class URLCreateView(APIView):
    """POST /api/v1/urls/ — create a shortened URL.

    Requires authentication. Tier logic is enforced inside URLCreateSerializer.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=URLCreateSerializer,
        responses={201: URLResponseSerializer},
        summary="Shorten a URL",
    )
    def post(self, request: Request) -> Response:
        serializer = URLCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        url = serializer.save(owner_id=request.user.pk)
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
    """GET /api/v1/urls/list/ — list the authenticated user's URLs.

    Supports optional tag filtering via ?tag=<name> query parameter.
    Results are paginated via DRF's default PageNumberPagination.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: URLResponseSerializer(many=True)},
        summary="List my shortened URLs",
        parameters=[
            OpenApiParameter(
                name="tag",
                location=OpenApiParameter.QUERY,
                description="Filter URLs by tag name (e.g. ?tag=Marketing)",
                required=False,
                type=str,
            )
        ],
    )
    def get(self, request: Request) -> Response:
        qs = (
            URL.objects.filter(owner_id=request.user.pk)
            .prefetch_related("tags")
            .order_by("-created_at")
        )
        tag_name: str | None = request.query_params.get("tag")
        if tag_name:
            qs = qs.filter(tags__name=tag_name)
        serializer = URLResponseSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class URLDetailView(APIView):
    """GET / PUT / DELETE /api/v1/urls/<short_code>/

    Module 8: PUT and DELETE now invalidate the Redis cache.
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
        self.check_object_permissions(request, url)
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

        # Module 8: Invalidate cache so the next redirect fetches fresh data.
        invalidate_url_cache(short_code)

        logger.info(
            "PUT /api/v1/urls/%s/ — updated by user=%r (cache invalidated)",
            short_code,
            request.user.username,
        )
        return Response(
            URLResponseSerializer(updated, context={"request": request}).data
        )

    @extend_schema(responses={204: None}, summary="Deactivate a URL (owner only)")
    def delete(self, request: Request, short_code: str) -> Response:
        url = self._get_url(short_code)
        self.check_object_permissions(request, url)
        url.is_active = False
        url.save(update_fields=["is_active", "updated_at"])

        # Module 8: Invalidate cache so the next redirect sees is_active=False.
        invalidate_url_cache(short_code)

        logger.info(
            "DELETE /api/v1/urls/%s/ — deactivated by user=%r (cache invalidated)",
            short_code,
            request.user.username,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RedirectView(APIView):
    """GET /<short_code>/ — public redirect endpoint.

    Module 8 changes:
      1. Cache-aside: check Redis first, fall back to DB on miss.
      2. Write-behind: Click creation is now async (Celery task).
         The redirect response is returned immediately.
         Analytics are written in the background.

    Performance:
      - Cache HIT:  ~2ms (Redis only, no DB)
      - Cache MISS: ~20ms (Redis + DB + cache write)
      - Before Mod8: ~50-100ms (DB read + 2 DB writes)
    """

    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, request: Request, short_code: str) -> HttpResponseRedirect:
        """Redirect to the original URL and queue analytics tracking.

        Cache-aside pattern:
          1. Check Redis for the URL.
          2. If miss, fetch from DB and populate cache.
          3. Validate is_active and is_expired.
          4. Queue Celery task for click tracking.
          5. Return 302 redirect immediately.
        """
        # Step 1 & 2: Cache-aside lookup.
        url = get_cached_url(short_code)

        if url is None:
            logger.warning("Redirect 404: short_code=%r not found", short_code)
            raise NotFound(f"Short link '{short_code}' not found.")

        # Step 3: Validate link state.
        try:
            if not url.is_active:
                raise ShortLinkInactiveError(short_code)
            if url.is_expired:
                raise ShortLinkExpiredError(short_code)
        except (ShortLinkInactiveError, ShortLinkExpiredError) as exc:
            logger.warning("Redirect blocked: %s", exc)
            raise NotFound(str(exc)) from exc

        # Step 4: Queue async click tracking (write-behind pattern).
        # The view does NOT wait for this — it returns immediately.
        ip = _get_client_ip(request)
        country, city = _geolocate_ip(ip)
        track_click.delay(
            url_id=url.pk,
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referrer=request.META.get("HTTP_REFERER") or None,
            country=country,
            city=city,
        )

        logger.info(
            "GET /%s/ — redirecting to %r (async click queued)",
            short_code,
            url.original_url,
        )

        # Step 5: Return redirect immediately (no DB writes in this request).
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
