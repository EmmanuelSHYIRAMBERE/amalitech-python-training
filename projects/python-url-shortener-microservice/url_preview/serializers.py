"""Serializers for the URL Preview microservice — Module 9."""

from rest_framework import serializers


class PreviewRequestSerializer(serializers.Serializer[dict]):  # type: ignore[type-arg]
    """Input: the URL to fetch preview metadata for."""

    url = serializers.URLField()


class PreviewResponseSerializer(serializers.Serializer[dict]):  # type: ignore[type-arg]
    """Output: scraped metadata from the destination page."""

    url         = serializers.URLField()
    title       = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    favicon     = serializers.URLField(allow_null=True, allow_blank=True)
    error       = serializers.CharField(allow_null=True, required=False)
