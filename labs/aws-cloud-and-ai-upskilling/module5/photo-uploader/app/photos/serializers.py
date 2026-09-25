"""camelCase response envelope -- must byte-match the Node app's Photo
shape so public/index.html's JS keeps working unmodified."""

from __future__ import annotations

from rest_framework import serializers

from .models import Photo
from .services import photo_url

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class PhotoSerializer(serializers.ModelSerializer):
    """Read-shape serializer -- output only, camelCase field names."""

    s3Key = serializers.CharField(source="s3_key", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ["id", "s3Key", "description", "createdAt", "url"]

    def get_url(self, obj: Photo) -> str:
        return photo_url(obj.s3_key)


class PhotoUploadSerializer(serializers.Serializer):
    """Input-shape serializer for POST /api/v1/photos -- validates the
    multipart 'photo' file field + 'description' text field."""

    photo = serializers.FileField(
        required=True,
        error_messages={"required": "No photo file provided"},
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            "required": "Description is required",
            "blank": "Description is required",
        },
    )

    def validate_photo(self, value):
        if value.content_type not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError(f"Unsupported file type: {value.content_type}")
        if value.size > MAX_UPLOAD_BYTES:
            raise serializers.ValidationError("File exceeds the 10MB size limit")
        return value

    def validate_description(self, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Description is required")
        return stripped
