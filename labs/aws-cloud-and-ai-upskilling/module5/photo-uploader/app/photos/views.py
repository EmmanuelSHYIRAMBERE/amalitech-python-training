"""Photo gallery views -- GET/POST /api/v1/photos."""

from __future__ import annotations

from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Photo
from .serializers import PhotoSerializer, PhotoUploadSerializer
from .services import upload_photo


class PhotoListCreateView(APIView):
    """GET  /api/v1/photos -- list all photos, newest first.
    POST /api/v1/photos -- upload a photo (multipart: photo file + description)."""

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request: Request) -> Response:
        photos = Photo.objects.all()  # Meta.ordering = -created_at
        return Response({"success": True, "data": PhotoSerializer(photos, many=True).data})

    def post(self, request: Request) -> Response:
        serializer = PhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        photo_file = serializer.validated_data["photo"]
        description = serializer.validated_data["description"]

        s3_key = upload_photo(
            file_bytes=photo_file.read(),
            mime_type=photo_file.content_type,
            original_name=photo_file.name,
        )
        photo = Photo.objects.create(s3_key=s3_key, description=description)

        return Response(
            {"success": True, "message": "Photo uploaded", "data": PhotoSerializer(photo).data},
            status=201,
        )
