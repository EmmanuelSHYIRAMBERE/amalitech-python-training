import logging
from typing import Any

from rest_framework import serializers
from rest_framework.request import Request

from .models import URL, generate_short_code

logger = logging.getLogger(__name__)


class URLCreateSerializer(serializers.ModelSerializer[URL]):
    class Meta:
        model = URL
        fields = ["original_url"]

    def create(self, validated_data: dict[str, Any]) -> URL:
        url = URL.objects.create(
            short_code=generate_short_code(),
            **validated_data,
        )
        logger.info("Created short_code=%r for original_url=%r", url.short_code, url.original_url)
        return url


class URLResponseSerializer(serializers.ModelSerializer[URL]):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = URL
        fields = ["short_code", "original_url", "short_url", "created_at"]

    def get_short_url(self, obj: URL) -> str:
        request: Request | None = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/{obj.short_code}/")
        return f"/{obj.short_code}/"
