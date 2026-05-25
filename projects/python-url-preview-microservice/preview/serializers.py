"""Serializers for the preview endpoints.

Contract: PreviewResponseSerializer must produce JSON identical to what
shortener/preview_client.py in the url-shortener service expects.
"""
from __future__ import annotations

from rest_framework import serializers


class PreviewRequestSerializer(serializers.Serializer):
    """Input: the URL to fetch preview metadata for."""

    url = serializers.URLField()


class PreviewResponseSerializer(serializers.Serializer):
    """Output: scraped metadata — matches PreviewResult dataclass shape."""

    url = serializers.URLField()
    title = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    favicon = serializers.URLField(allow_null=True, allow_blank=True)
    error = serializers.CharField(allow_null=True, required=False)
