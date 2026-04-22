import logging

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import URL
from .serializers import URLCreateSerializer, URLResponseSerializer

logger = logging.getLogger(__name__)


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
        url = get_object_or_404(URL, short_code=short_code)
        logger.info("GET /%s/ — redirecting to %r", short_code, url.original_url)
        return HttpResponseRedirect(url.original_url)
