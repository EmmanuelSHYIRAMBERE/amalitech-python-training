"""Tests for shortener.views — URLCreateView (POST) and RedirectView (GET)."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from shortener.generators import SecureShortCodeGenerator
from shortener.models import URL
from shortener.serializers import URLCreateSerializer


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
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "short_code" in response.data
    assert response.data["short_code"]


@pytest.mark.django_db
def test_create_url_response_contains_short_url(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "short_url" in response.data
    assert response.data["short_url"]


@pytest.mark.django_db
def test_create_url_response_contains_original_url(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.data["original_url"] == sample_url_data["original_url"]


@pytest.mark.django_db
def test_create_url_response_contains_created_at(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "created_at" in response.data
    assert response.data["created_at"]


@pytest.mark.django_db
def test_create_url_persists_to_database(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    assert URL.objects.count() == 0
    api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert URL.objects.count() == 1


@pytest.mark.django_db
def test_create_url_short_code_is_six_chars(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert len(response.data["short_code"]) == 6


@pytest.mark.django_db
def test_create_url_with_injected_generator(
    api_client: APIClient, sample_url_data: dict[str, str], mocker
) -> None:
    """Generator injected via Protocol DI must be called and its value used."""
    mock_gen = mocker.MagicMock(return_value="mocked1")
    mocker.patch("shortener.serializers.default_generator", mock_gen)
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["short_code"] == "mocked1"


@pytest.mark.django_db
def test_create_url_missing_body_returns_400(api_client: APIClient) -> None:
    response = api_client.post("/api/v1/urls/", {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_url_missing_body_error_references_field(api_client: APIClient) -> None:
    response = api_client.post("/api/v1/urls/", {}, format="json")
    assert "original_url" in response.data


@pytest.mark.parametrize(
    "bad_url",
    [
        "not-a-url",
        "",
        "just text",
        "http://",
        # ftp:// now rejected by validate_url_scheme regex validator
        "ftp://example.com",
    ],
)
@pytest.mark.django_db
def test_create_url_invalid_url_returns_400(
    api_client: APIClient, bad_url: str
) -> None:
    """Malformed URLs and non-http/https schemes must return HTTP 400."""
    response = api_client.post(
        "/api/v1/urls/", {"original_url": bad_url}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_url_short_url_is_absolute_uri(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.data["short_url"].startswith("http")


# ---------------------------------------------------------------------------
# RedirectView — GET /<short_code>/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_returns_302(api_client: APIClient, created_url: URL) -> None:
    response = api_client.get(f"/{created_url.short_code}/")
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_redirect_location_header_is_original_url(
    api_client: APIClient, created_url: URL
) -> None:
    response = api_client.get(f"/{created_url.short_code}/")
    assert response["Location"] == created_url.original_url


@pytest.mark.django_db
def test_redirect_unknown_code_returns_404(api_client: APIClient) -> None:
    response = api_client.get("/doesnotexist/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_redirect_uses_correct_original_url() -> None:
    target = "https://www.specific-target.com/path"
    URL.objects.create(original_url=target, short_code="tgt001")
    client = APIClient()
    response = client.get("/tgt001/")
    assert response["Location"] == target


@pytest.mark.django_db
def test_redirect_does_not_follow_redirect_by_default(
    api_client: APIClient, created_url: URL
) -> None:
    response = api_client.get(f"/{created_url.short_code}/")
    assert response.status_code != status.HTTP_200_OK
