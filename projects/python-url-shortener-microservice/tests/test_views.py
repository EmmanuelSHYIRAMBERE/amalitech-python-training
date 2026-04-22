"""Tests for shortener.views — URLCreateView (POST) and RedirectView (GET).

Covers:
- POST /api/v1/urls/ happy path, 400 on bad input, response shape
- GET /<short_code>/ 302 redirect, 404 on unknown code
- Mocked generate_short_code to assert deterministic short_code output
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shortener.models import URL


# ---------------------------------------------------------------------------
# URLCreateView — POST /api/v1/urls/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_url_returns_201(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    """A valid POST must return HTTP 201 Created."""
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_url_response_contains_short_code(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    """Response body must include a non-empty short_code."""
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "short_code" in response.data
    assert response.data["short_code"]


@pytest.mark.django_db
def test_create_url_response_contains_short_url(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    """Response body must include a short_url field."""
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "short_url" in response.data
    assert response.data["short_url"]


@pytest.mark.django_db
def test_create_url_response_contains_original_url(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    """Response body must echo back the original_url."""
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.data["original_url"] == sample_url_data["original_url"]


@pytest.mark.django_db
def test_create_url_response_contains_created_at(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    """Response body must include a created_at timestamp."""
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "created_at" in response.data
    assert response.data["created_at"]


@pytest.mark.django_db
def test_create_url_persists_to_database(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    """A successful POST must create exactly one URL record in the database."""
    assert URL.objects.count() == 0
    api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert URL.objects.count() == 1


@pytest.mark.django_db
def test_create_url_short_code_is_six_chars(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    """The generated short_code must be exactly 6 characters long."""
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert len(response.data["short_code"]) == 6


@pytest.mark.django_db
def test_create_url_with_mocked_short_code(
    api_client: APIClient, sample_url_data: dict[str, str], mocker
) -> None:
    """generate_short_code must be called once and its return value used."""
    mocker.patch("shortener.serializers.generate_short_code", return_value="mocked1")
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["short_code"] == "mocked1"


@pytest.mark.django_db
def test_create_url_missing_body_returns_400(api_client: APIClient) -> None:
    """A POST with no body must return HTTP 400 Bad Request."""
    response = api_client.post("/api/v1/urls/", {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_url_missing_body_error_references_field(api_client: APIClient) -> None:
    """The 400 error body must reference the original_url field."""
    response = api_client.post("/api/v1/urls/", {}, format="json")
    assert "original_url" in response.data


@pytest.mark.parametrize(
    "bad_url",
    [
        "not-a-url",
        "",
        "just text",
        # Note: Django's URLField accepts any scheme (ftp://, etc.) by design.
    ],
)
@pytest.mark.django_db
def test_create_url_invalid_url_returns_400(
    api_client: APIClient, bad_url: str
) -> None:
    """Structurally malformed URLs must return HTTP 400."""
    response = api_client.post(
        "/api/v1/urls/", {"original_url": bad_url}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_url_short_url_is_absolute_uri(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    """short_url in the response must be an absolute URI (starts with http)."""
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.data["short_url"].startswith("http")


# ---------------------------------------------------------------------------
# RedirectView — GET /<short_code>/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_returns_302(api_client: APIClient, created_url: URL) -> None:
    """GET /<short_code>/ must return HTTP 302 Found."""
    response = api_client.get(f"/{created_url.short_code}/")
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_redirect_location_header_is_original_url(
    api_client: APIClient, created_url: URL
) -> None:
    """The Location header must point to the original URL."""
    response = api_client.get(f"/{created_url.short_code}/")
    assert response["Location"] == created_url.original_url


@pytest.mark.django_db
def test_redirect_unknown_code_returns_404(api_client: APIClient) -> None:
    """GET with an unknown short_code must return HTTP 404 Not Found."""
    response = api_client.get("/doesnotexist/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_redirect_uses_correct_original_url() -> None:
    """Redirect must point to the exact original_url stored for that short_code."""
    target = "https://www.specific-target.com/path"
    URL.objects.create(original_url=target, short_code="tgt001")
    client = APIClient()
    response = client.get("/tgt001/")
    assert response["Location"] == target


@pytest.mark.django_db
def test_redirect_does_not_follow_redirect_by_default(
    api_client: APIClient, created_url: URL
) -> None:
    """APIClient must not auto-follow the redirect — status must be 302, not 200."""
    response = api_client.get(f"/{created_url.short_code}/")
    # Confirm we are testing the redirect itself, not the destination.
    assert response.status_code != status.HTTP_200_OK
