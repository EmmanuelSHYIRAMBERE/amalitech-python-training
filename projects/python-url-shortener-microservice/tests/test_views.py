"""Tests for shortener.views — Module 5 + Module 6."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from shortener.models import URL, Click
from shortener.serializers import URLCreateSerializer
from users.models import User

# ---------------------------------------------------------------------------
# URLCreateView — POST /api/v1/urls/ (Mod 5, unchanged)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_url_returns_201(
    api_client: APIClient, sample_url_data: dict[str, str]
) -> None:
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
    mock_gen = mocker.MagicMock(return_value="mocked1")
    original_init = URLCreateSerializer.__init__

    def patched_init(self, *args, **kwargs):
        kwargs.setdefault("generator", mock_gen)
        original_init(self, *args, **kwargs)

    mocker.patch.object(URLCreateSerializer, "__init__", patched_init)
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
    ["not-a-url", "", "just text", "http://", "ftp://example.com"],
)
@pytest.mark.django_db
def test_create_url_invalid_url_returns_400(
    api_client: APIClient, bad_url: str
) -> None:
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
# RedirectView — GET /<short_code>/ (Mod 5, unchanged)
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
def test_redirect_uses_correct_original_url(user: User) -> None:
    target = "https://www.specific-target.com/path"
    URL.objects.create(original_url=target, short_code="tgt001", owner=user)
    client = APIClient()
    response = client.get("/tgt001/")
    assert response["Location"] == target


@pytest.mark.django_db
def test_redirect_does_not_follow_redirect_by_default(
    api_client: APIClient, created_url: URL
) -> None:
    response = api_client.get(f"/{created_url.short_code}/")
    assert response.status_code != status.HTTP_200_OK


# ---------------------------------------------------------------------------
# RedirectView — Mod 6 behaviour
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_logs_click(api_client: APIClient, created_url: URL) -> None:
    """Every redirect must create a Click record."""
    assert Click.objects.count() == 0
    api_client.get(f"/{created_url.short_code}/")
    assert Click.objects.count() == 1


@pytest.mark.django_db
def test_redirect_increments_click_count(
    api_client: APIClient, created_url: URL
) -> None:
    api_client.get(f"/{created_url.short_code}/")
    created_url.refresh_from_db()
    assert created_url.click_count == 1


@pytest.mark.django_db
def test_redirect_inactive_url_returns_404(api_client: APIClient, user: User) -> None:
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="inact2",
        owner=user,
        is_active=False,
    )
    response = api_client.get(f"/{url.short_code}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_redirect_expired_url_returns_404(api_client: APIClient, user: User) -> None:
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="exprd3",
        owner=user,
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    response = api_client.get(f"/{url.short_code}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_redirect_click_stores_user_agent(
    api_client: APIClient, created_url: URL
) -> None:
    api_client.get(
        f"/{created_url.short_code}/",
        HTTP_USER_AGENT="TestBrowser/1.0",
    )
    click = Click.objects.first()
    assert click is not None
    assert click.user_agent == "TestBrowser/1.0"


@pytest.mark.django_db
def test_redirect_click_stores_referrer(
    api_client: APIClient, created_url: URL
) -> None:
    api_client.get(
        f"/{created_url.short_code}/",
        HTTP_REFERER="https://google.com",
    )
    click = Click.objects.first()
    assert click is not None
    assert click.referrer == "https://google.com"


# ---------------------------------------------------------------------------
# URLAnalyticsView — GET /api/v1/analytics/<short_code>/ (Mod 6)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_analytics_returns_200(api_client: APIClient, created_url: URL) -> None:
    response = api_client.get(f"/api/v1/analytics/{created_url.short_code}/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analytics_contains_click_count(
    api_client: APIClient, created_url: URL
) -> None:
    response = api_client.get(f"/api/v1/analytics/{created_url.short_code}/")
    assert "click_count" in response.data


@pytest.mark.django_db
def test_analytics_contains_clicks_by_country(
    api_client: APIClient, created_url: URL
) -> None:
    Click.objects.create(
        url=created_url, ip_address="1.1.1.1", user_agent="ua", country="RW"
    )
    response = api_client.get(f"/api/v1/analytics/{created_url.short_code}/")
    assert "clicks_by_country" in response.data
    assert response.data["clicks_by_country"][0]["country"] == "RW"
    assert response.data["clicks_by_country"][0]["total"] == 1


@pytest.mark.django_db
def test_analytics_unknown_code_returns_404(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/analytics/unknown1/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Collision retry — ShortCodeCollisionError (best-practices addition)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_url_raises_500_on_collision_exhaustion(
    api_client: APIClient, sample_url_data: dict[str, str], mocker
) -> None:
    """When all 5 retry attempts collide, DRF returns 500 (unhandled app error).

    ShortCodeCollisionError is not a DRF exception so it propagates as a 500.
    Mod 7 will add an exception_handler to convert it to 503 Service Unavailable.
    """
    from django.db import IntegrityError
    from shortener.exceptions import ShortCodeCollisionError

    mocker.patch(
        "shortener.serializers.URL.objects.create",
        side_effect=IntegrityError("duplicate key"),
    )
    # Disable Django test client's exception re-raise so we get the HTTP response.
    api_client.raise_request_exception = False
    response = api_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.status_code == 500


# ---------------------------------------------------------------------------
# transaction.atomic — Click + click_count atomicity (best-practices addition)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_click_and_count_are_atomic(
    api_client: APIClient, created_url: URL, mocker
) -> None:
    """If increment_click_count raises, the Click row must also be rolled back."""
    mocker.patch.object(
        created_url.__class__,
        "increment_click_count",
        side_effect=Exception("DB failure"),
    )
    # Patch get_object_or_404 to return our controlled instance.
    mocker.patch(
        "shortener.views.get_object_or_404",
        return_value=created_url,
    )
    with pytest.raises(Exception, match="DB failure"):
        api_client.get(f"/{created_url.short_code}/")

    # The transaction rolled back — no Click row should exist.
    assert Click.objects.filter(url=created_url).count() == 0


# ---------------------------------------------------------------------------
# Named exceptions in RedirectView (best-practices addition)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_inactive_returns_404_with_detail(
    api_client: APIClient, user: User
) -> None:
    """404 response for inactive link must include the short_code in detail."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="inact9",
        owner=user,
        is_active=False,
    )
    response = api_client.get(f"/{url.short_code}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "inact9" in str(response.data)


@pytest.mark.django_db
def test_redirect_expired_returns_404_with_detail(
    api_client: APIClient, user: User
) -> None:
    """404 response for expired link must include the short_code in detail."""
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="exprd9",
        owner=user,
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    response = api_client.get(f"/{url.short_code}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "exprd9" in str(response.data)
