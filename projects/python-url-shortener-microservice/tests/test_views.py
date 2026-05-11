"""Tests for shortener.views — Module 5 + Module 6 + Module 7 + Module 8.

Module 7 changes:
  - URLCreateView now requires authentication → use auth_client fixture.
  - URLAnalyticsView is premium-only → use premium_auth_client fixture.
  - RedirectView remains public → api_client (unauthenticated) still used.

Module 8 changes:
  - RedirectView now uses cache-aside (get_cached_url) and async tasks.
  - Click records are created by Celery task, not in the view.
  - Tests mock get_cached_url and track_click.delay.
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from shortener.models import URL, Click
from shortener.serializers import URLCreateSerializer
from users.models import User

# ---------------------------------------------------------------------------
# URLCreateView — POST /api/v1/urls/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_url_returns_201(
    auth_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_url_response_contains_short_code(
    auth_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "short_code" in response.data
    assert response.data["short_code"]


@pytest.mark.django_db
def test_create_url_response_contains_short_url(
    auth_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "short_url" in response.data
    assert response.data["short_url"]


@pytest.mark.django_db
def test_create_url_response_contains_original_url(
    auth_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.data["original_url"] == sample_url_data["original_url"]


@pytest.mark.django_db
def test_create_url_response_contains_created_at(
    auth_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert "created_at" in response.data
    assert response.data["created_at"]


@pytest.mark.django_db
def test_create_url_persists_to_database(
    auth_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    assert URL.objects.count() == 0
    auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert URL.objects.count() == 1


@pytest.mark.django_db
def test_create_url_short_code_is_six_chars(
    auth_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert len(response.data["short_code"]) == 6


@pytest.mark.django_db
def test_create_url_with_injected_generator(
    auth_client: APIClient, sample_url_data: dict[str, str], mocker
) -> None:
    mock_gen = mocker.MagicMock(return_value="mocked1")
    original_init = URLCreateSerializer.__init__

    def patched_init(self, *args, **kwargs):
        kwargs.setdefault("generator", mock_gen)
        original_init(self, *args, **kwargs)

    mocker.patch.object(URLCreateSerializer, "__init__", patched_init)
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["short_code"] == "mocked1"


@pytest.mark.django_db
def test_create_url_missing_body_returns_400(auth_client: APIClient) -> None:
    response = auth_client.post("/api/v1/urls/", {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_url_missing_body_error_references_field(auth_client: APIClient) -> None:
    response = auth_client.post("/api/v1/urls/", {}, format="json")
    assert "original_url" in response.data


@pytest.mark.parametrize(
    "bad_url",
    ["not-a-url", "", "just text", "http://", "ftp://example.com"],
)
@pytest.mark.django_db
def test_create_url_invalid_url_returns_400(
    auth_client: APIClient, bad_url: str
) -> None:
    response = auth_client.post(
        "/api/v1/urls/", {"original_url": bad_url}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_url_short_url_is_absolute_uri(
    auth_client: APIClient, sample_url_data: dict[str, str]
) -> None:
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.data["short_url"].startswith("http")


# ---------------------------------------------------------------------------
# RedirectView — GET /<short_code>/ (public — unauthenticated api_client)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_returns_302(api_client: APIClient, created_url: URL) -> None:
    with patch("shortener.views.track_click.delay"):
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
# RedirectView — Mod 6 behaviour (public)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_queues_click_task(api_client: APIClient, created_url: URL) -> None:
    """Module 8: Every redirect must queue a Celery task (not write synchronously)."""
    with (
        patch("shortener.views.track_click.delay") as mock_task,
        patch("shortener.views.get_cached_url", return_value=created_url),
    ):
        api_client.get(f"/{created_url.short_code}/")
    mock_task.assert_called_once()


@pytest.mark.django_db
def test_redirect_click_task_receives_url_id(
    api_client: APIClient, created_url: URL
) -> None:
    """Module 8: The queued task must receive the correct url_id."""
    with (
        patch("shortener.views.track_click.delay") as mock_task,
        patch("shortener.views.get_cached_url", return_value=created_url),
    ):
        api_client.get(f"/{created_url.short_code}/")
    call_kwargs = mock_task.call_args.kwargs
    assert call_kwargs["url_id"] == created_url.pk


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
    """Module 8: user_agent is forwarded to the async Celery task."""
    with patch("shortener.views.track_click.delay") as mock_task:
        api_client.get(
            f"/{created_url.short_code}/",
            HTTP_USER_AGENT="TestBrowser/1.0",
        )
    mock_task.assert_called_once()
    assert mock_task.call_args.kwargs["user_agent"] == "TestBrowser/1.0"


@pytest.mark.django_db
def test_redirect_click_stores_referrer(
    api_client: APIClient, created_url: URL
) -> None:
    """Module 8: referrer is forwarded to the async Celery task."""
    with patch("shortener.views.track_click.delay") as mock_task:
        api_client.get(
            f"/{created_url.short_code}/",
            HTTP_REFERER="https://google.com",
        )
    mock_task.assert_called_once()
    assert mock_task.call_args.kwargs["referrer"] == "https://google.com"


# ---------------------------------------------------------------------------
# URLAnalyticsView — GET /api/v1/analytics/<short_code>/ (premium only)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_analytics_returns_200(
    premium_auth_client: APIClient, created_url: URL
) -> None:
    response = premium_auth_client.get(f"/api/v1/analytics/{created_url.short_code}/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analytics_contains_click_count(
    premium_auth_client: APIClient, created_url: URL
) -> None:
    response = premium_auth_client.get(f"/api/v1/analytics/{created_url.short_code}/")
    assert "click_count" in response.data


@pytest.mark.django_db
def test_analytics_contains_clicks_by_country(
    premium_auth_client: APIClient, created_url: URL
) -> None:
    Click.objects.create(
        url=created_url, ip_address="1.1.1.1", user_agent="ua", country="RW"
    )
    response = premium_auth_client.get(f"/api/v1/analytics/{created_url.short_code}/")
    assert "clicks_by_country" in response.data
    assert response.data["clicks_by_country"][0]["country"] == "RW"
    assert response.data["clicks_by_country"][0]["total"] == 1


@pytest.mark.django_db
def test_analytics_unknown_code_returns_404(premium_auth_client: APIClient) -> None:
    response = premium_auth_client.get("/api/v1/analytics/unknown1/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Collision retry — ShortCodeCollisionError
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_url_raises_500_on_collision_exhaustion(
    auth_client: APIClient, sample_url_data: dict[str, str], mocker
) -> None:
    """When all 5 retry attempts collide, DRF returns 500 (unhandled app error)."""
    from django.db import IntegrityError

    mocker.patch(
        "shortener.serializers.URL.objects.create",
        side_effect=IntegrityError("duplicate key"),
    )
    auth_client.raise_request_exception = False
    response = auth_client.post("/api/v1/urls/", sample_url_data, format="json")
    assert response.status_code == 500


# ---------------------------------------------------------------------------
# transaction.atomic — Click + click_count atomicity
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_does_not_write_click_synchronously(
    api_client: APIClient, created_url: URL
) -> None:
    """Module 8: RedirectView never writes Click rows — tracking is async via Celery."""
    with patch("shortener.views.track_click.delay"):
        api_client.get(f"/{created_url.short_code}/")
    assert Click.objects.filter(url=created_url).count() == 0


# ---------------------------------------------------------------------------
# Named exceptions in RedirectView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_inactive_returns_404_with_detail(
    api_client: APIClient, user: User
) -> None:
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
    url = URL.objects.create(
        original_url="https://example.com",
        short_code="exprd9",
        owner=user,
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    response = api_client.get(f"/{url.short_code}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "exprd9" in str(response.data)
