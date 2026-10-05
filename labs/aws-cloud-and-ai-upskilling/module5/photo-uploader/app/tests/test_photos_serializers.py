import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from photos.models import Photo
from photos.serializers import PhotoSerializer, PhotoUploadSerializer


@pytest.mark.django_db
def test_photo_serializer_produces_camelcase_envelope(settings):
    settings.CLOUDFRONT_DOMAIN = "abc123.cloudfront.net"
    photo = Photo.objects.create(s3_key="photos/foo.jpg", description="A test photo")

    data = PhotoSerializer(photo).data

    assert set(data.keys()) == {"id", "s3Key", "description", "createdAt", "url"}
    assert data["s3Key"] == "photos/foo.jpg"
    assert data["url"] == "https://abc123.cloudfront.net/photos/foo.jpg"


def test_upload_serializer_rejects_missing_photo():
    serializer = PhotoUploadSerializer(data={"description": "test"})
    assert not serializer.is_valid()
    assert str(serializer.errors["photo"][0]) == "No photo file provided"


def test_upload_serializer_rejects_missing_description():
    photo_file = SimpleUploadedFile("test.jpg", b"fake", content_type="image/jpeg")
    serializer = PhotoUploadSerializer(data={"photo": photo_file, "description": ""})
    assert not serializer.is_valid()
    assert str(serializer.errors["description"][0]) == "Description is required"


def test_upload_serializer_rejects_bad_mime_type():
    photo_file = SimpleUploadedFile("test.txt", b"fake", content_type="text/plain")
    serializer = PhotoUploadSerializer(data={"photo": photo_file, "description": "test"})
    assert not serializer.is_valid()
    assert "Unsupported file type" in str(serializer.errors["photo"][0])


def test_upload_serializer_accepts_valid_input():
    photo_file = SimpleUploadedFile("test.jpg", b"fake", content_type="image/jpeg")
    serializer = PhotoUploadSerializer(data={"photo": photo_file, "description": "  A photo  "})
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["description"] == "A photo"
