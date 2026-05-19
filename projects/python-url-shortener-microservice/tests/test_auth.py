"""Tests for Module 7 — Authentication, Authorization, and Tier Logic."""

from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from shortener.models import URL
from users.models import User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def auth_client(user: User) -> APIClient:
    """Return an APIClient with a valid JWT Bearer token for ``user``."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_register_returns_201(api_client: APIClient) -> None:
    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    response = api_client.post("/api/v1/auth/register/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_register_returns_user_profile(api_client: APIClient) -> None:
    payload = {
        "username": "newuser2",
        "email": "new2@example.com",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    response = api_client.post("/api/v1/auth/register/", payload, format="json")
    assert response.data["username"] == "newuser2"
    assert response.data["tier"] == "Free"
    assert "password" not in response.data


@pytest.mark.django_db
def test_register_password_mismatch_returns_400(api_client: APIClient) -> None:
    payload = {
        "username": "baduser",
        "email": "bad@example.com",
        "password": "StrongPass123!",
        "password2": "WrongPass456!",
    }
    response = api_client.post("/api/v1/auth/register/", payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data


@pytest.mark.django_db
def test_register_duplicate_email_returns_400(
    api_client: APIClient, user: User
) -> None:
    payload = {
        "username": "other",
        "email": user.email,
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    response = api_client.post("/api/v1/auth/register/", payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_returns_tokens(api_client: APIClient, user: User) -> None:
    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "testpass123"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_returns_user_profile(api_client: APIClient, user: User) -> None:
    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "testpass123"},
        format="json",
    )
    assert response.data["user"]["username"] == user.username


@pytest.mark.django_db
def test_login_wrong_password_returns_401(api_client: APIClient, user: User) -> None:
    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "wrongpassword"},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_login_unknown_user_returns_401(api_client: APIClient) -> None:
    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": "ghost", "password": "whatever"},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Token Refresh
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_token_refresh_returns_new_access(api_client: APIClient, user: User) -> None:
    refresh = RefreshToken.for_user(user)
    response = api_client.post(
        "/api/v1/auth/refresh/",
        {"refresh": str(refresh)},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


# ---------------------------------------------------------------------------
# URLCreateView — authentication required
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_url_unauthenticated_returns_401(api_client: APIClient) -> None:
    response = api_client.post(
        "/api/v1/urls/", {"original_url": "https://example.com"}, format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_url_authenticated_returns_201(user: User) -> None:
    client = auth_client(user)
    response = client.post(
        "/api/v1/urls/", {"original_url": "https://example.com"}, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_url_sets_owner(user: User) -> None:
    client = auth_client(user)
    client.post("/api/v1/urls/", {"original_url": "https://example.com"}, format="json")
    url = URL.objects.first()
    assert url is not None
    assert url.owner == user


# ---------------------------------------------------------------------------
# Tier logic — Free user quota
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_free_user_cannot_exceed_10_urls(user: User) -> None:
    for i in range(10):
        URL.objects.create(
            original_url=f"https://example{i}.com",
            short_code=f"free{i:04d}",
            owner=user,
            is_active=True,
        )
    client = auth_client(user)
    response = client.post(
        "/api/v1/urls/", {"original_url": "https://eleventh.com"}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "10" in str(response.data)


@pytest.mark.django_db
def test_premium_user_can_exceed_10_urls(premium_user: User) -> None:
    for i in range(10):
        URL.objects.create(
            original_url=f"https://example{i}.com",
            short_code=f"prem{i:04d}",
            owner=premium_user,
            is_active=True,
        )
    client = auth_client(premium_user)
    response = client.post(
        "/api/v1/urls/", {"original_url": "https://eleventh.com"}, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED


# ---------------------------------------------------------------------------
# Tier logic — custom alias
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_free_user_cannot_use_custom_alias(user: User) -> None:
    client = auth_client(user)
    response = client.post(
        "/api/v1/urls/",
        {"original_url": "https://example.com", "custom_alias": "my-shop"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "custom_alias" in response.data


@pytest.mark.django_db
def test_premium_user_can_use_custom_alias(premium_user: User) -> None:
    client = auth_client(premium_user)
    response = client.post(
        "/api/v1/urls/",
        {"original_url": "https://example.com", "custom_alias": "my-shop"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_alias"] == "my-shop"


# ---------------------------------------------------------------------------
# URLListView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_list_urls_returns_only_own_urls(user: User, premium_user: User) -> None:
    URL.objects.create(original_url="https://a.com", short_code="own001", owner=user)
    URL.objects.create(
        original_url="https://b.com", short_code="oth001", owner=premium_user
    )
    client = auth_client(user)
    response = client.get("/api/v1/urls/list/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["short_code"] == "own001"


@pytest.mark.django_db
def test_list_urls_filter_by_tag(user: User) -> None:
    """GET /api/v1/urls/list/?tag=Marketing returns only URLs with that tag."""
    from shortener.models import Tag

    tag, _ = Tag.objects.get_or_create(name="Marketing")
    url_with_tag = URL.objects.create(
        original_url="https://tagged.com", short_code="tag001", owner=user
    )
    url_with_tag.tags.add(tag)
    URL.objects.create(
        original_url="https://untagged.com", short_code="tag002", owner=user
    )
    client = auth_client(user)
    response = client.get("/api/v1/urls/list/?tag=Marketing")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["short_code"] == "tag001"


@pytest.mark.django_db
def test_list_urls_filter_by_nonexistent_tag_returns_empty(user: User) -> None:
    URL.objects.create(original_url="https://a.com", short_code="tag003", owner=user)
    client = auth_client(user)
    response = client.get("/api/v1/urls/list/?tag=DoesNotExist")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.django_db
def test_list_urls_unauthenticated_returns_401(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/urls/list/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# URLDetailView — IsOwnerOrReadOnly
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_detail_get_returns_200(user: User, created_url: URL) -> None:
    client = auth_client(user)
    response = client.get(f"/api/v1/urls/{created_url.short_code}/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_detail_delete_by_owner_returns_204(user: User, created_url: URL) -> None:
    client = auth_client(user)
    response = client.delete(f"/api/v1/urls/{created_url.short_code}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    created_url.refresh_from_db()
    assert created_url.is_active is False


@pytest.mark.django_db
def test_detail_delete_by_non_owner_returns_403(
    premium_user: User, created_url: URL
) -> None:
    client = auth_client(premium_user)
    response = client.delete(f"/api/v1/urls/{created_url.short_code}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_detail_put_by_non_owner_returns_403(
    premium_user: User, created_url: URL
) -> None:
    client = auth_client(premium_user)
    response = client.put(
        f"/api/v1/urls/{created_url.short_code}/",
        {"original_url": "https://hacked.com"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# URLAnalyticsView — premium only
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_analytics_free_user_returns_403(user: User, created_url: URL) -> None:
    client = auth_client(user)
    response = client.get(f"/api/v1/analytics/{created_url.short_code}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_analytics_premium_user_returns_200(
    premium_user: User, created_url: URL
) -> None:
    client = auth_client(premium_user)
    response = client.get(f"/api/v1/analytics/{created_url.short_code}/")
    assert response.status_code == status.HTTP_200_OK
    assert "clicks_by_country" in response.data


# ---------------------------------------------------------------------------
# Redirect — remains public
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_redirect_is_public(api_client: APIClient, created_url: URL) -> None:
    """Unauthenticated users must still be able to follow short links."""
    with patch("shortener.views.track_click.delay"):
        response = api_client.get(f"/{created_url.short_code}/")
    assert response.status_code == status.HTTP_302_FOUND
