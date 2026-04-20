from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import URL
from .serializers import URLCreateSerializer, URLResponseSerializer


class URLCreateView(APIView):
    @extend_schema(
        request=URLCreateSerializer,
        responses={201: URLResponseSerializer},
        summary="Shorten a URL",
    )
    def post(self, request):
        serializer = URLCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.save()
        return Response(
            URLResponseSerializer(url, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class RedirectView(APIView):
    @extend_schema(exclude=True)
    def get(self, request, short_code: str):
        url = get_object_or_404(URL, short_code=short_code)
        return HttpResponseRedirect(url.original_url)
