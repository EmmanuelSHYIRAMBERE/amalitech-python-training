"""DRF serializers for the shortener app.

URLCreateSerializer accepts a ShortCodeGenerator via dependency injection
(satisfying the ShortCodeGenerator Protocol) — making the generator
swappable and mockable without subclassing, exactly as WeatherService
accepts a WeatherProvider in the TDD weather lab.
"""

import logging
from typing import Any

from rest_framework import serializers
from rest_framework.request import Request

from .generators import default_generator
from .models import URL
from .protocols import ShortCodeGenerator
from .validators import validate_url_scheme

logger = logging.getLogger(__name__)


class URLCreateSerializer(serializers.ModelSerializer[URL]):
    """Serializer for creating a shortened URL.

    Args:
        generator: Any object satisfying ``ShortCodeGenerator`` Protocol.
                   Defaults to ``default_generator`` (SecureShortCodeGenerator).
                   Pass a custom generator in tests or alternative implementations.
    """

    def __init__(self, *args: Any, generator: ShortCodeGenerator = default_generator, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._generator = generator

    class Meta:
        model = URL
        fields = ["original_url"]

    def validate_original_url(self, value: str) -> str:
        """Enforce http/https scheme using compiled regex (beyond Django's URLField)."""
        if not validate_url_scheme(value):
            raise serializers.ValidationError(
                "URL must use http:// or https:// scheme."
            )
        return value

    def create(self, validated_data: dict[str, Any]) -> URL:
        short_code = self._generator(length=6)
        url = URL.objects.create(short_code=short_code, **validated_data)
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
