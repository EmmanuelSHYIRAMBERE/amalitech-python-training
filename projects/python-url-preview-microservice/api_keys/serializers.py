"""Serializers for API key management endpoints."""
from __future__ import annotations

from rest_framework import serializers

from .models import APIKey


class APIKeyCreateSerializer(serializers.Serializer):
    """Input: a friendly name for the new key."""

    name = serializers.CharField(max_length=100)


class APIKeyResponseSerializer(serializers.ModelSerializer):
    """Output when a key is created — includes the raw token ONCE."""

    token = serializers.CharField(read_only=True)

    class Meta:
        model = APIKey
        fields = ["id", "name", "token", "created_at"]


class APIKeyListSerializer(serializers.ModelSerializer):
    """Read-only listing — never exposes the token."""

    class Meta:
        model = APIKey
        fields = [
            "id",
            "name",
            "is_active",
            "request_count",
            "last_used_at",
            "revoked_at",
            "created_at",
        ]
