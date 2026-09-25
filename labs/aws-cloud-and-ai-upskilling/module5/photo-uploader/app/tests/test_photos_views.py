from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from photos.models import Photo


@pytest.mark.django_db
def test_get_photos_returns_ordered_envelope(api_client):
    Photo.objects.create(s3_key="photos/first.jpg", description="first")
    Photo.objects.create(s3_key="photos/second.jpg", description="second")

    response = api_client.get("/api/v1/photos")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert [p["description"] for p in body["data"]] == ["second", "first"]


@pytest.mark.django_db
@patch("photos.views.upload_photo", return_value="photos/mocked.jpg")
def test_post_photo_happy_path(mock_upload, api_client):
    photo_file = SimpleUploadedFile("test.jpg", b"fake-bytes", content_type="image/jpeg")

    response = api_client.post(
        "/api/v1/photos",
        {"photo": photo_file, "description": "A test upload"},
        format="multipart",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Photo uploaded"
    assert body["data"]["s3Key"] == "photos/mocked.jpg"
    assert Photo.objects.count() == 1


@pytest.mark.django_db
def test_post_photo_missing_file_returns_400(api_client):
    response = api_client.post("/api/v1/photos", {"description": "test"}, format="multipart")
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["statusCode"] == 400
    assert body["message"] == "No photo file provided"


@pytest.mark.django_db
def test_post_photo_missing_description_returns_400(api_client):
    photo_file = SimpleUploadedFile("test.jpg", b"fake-bytes", content_type="image/jpeg")
    response = api_client.post("/api/v1/photos", {"photo": photo_file}, format="multipart")
    assert response.status_code == 400
    assert response.json()["message"] == "Description is required"


@pytest.mark.django_db
def test_post_photo_bad_mime_returns_clean_400(api_client):
    bad_file = SimpleUploadedFile("test.txt", b"fake-bytes", content_type="text/plain")
    response = api_client.post(
        "/api/v1/photos", {"photo": bad_file, "description": "test"}, format="multipart"
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["message"]


def test_unknown_route_returns_json_404(api_client):
    response = api_client.get("/nonexistent-route")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["statusCode"] == 404
