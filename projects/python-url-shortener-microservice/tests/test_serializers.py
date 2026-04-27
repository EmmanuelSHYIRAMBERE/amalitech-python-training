"""Tests for shortener.serializers — Module 5 + Module 6."""

import pytest
from rest_framework.test import APIRequestFactory

from shortener.models import Click, Tag, URL
from shortener.serializers import (
    URLAnalyticsSerializer,
    URLCreateSerializer,
    URLResponseSerializer,
)
from users.models import User

# ---------------------------------------------------------------------------
# URLCreateSerializer — validation (Mod 5, unchanged)
# ---------------------------------------------------------------------------


def test_create_serializer_valid_url_is_valid() -> None:
    serializer = URLCreateSerializer(data={"original_url": "https://www.example.com"})
    assert serializer.is_valid(), serializer.errors


def test_create_serializer_missing_url_is_invalid() -> None:
    serializer = URLCreateSerializer(data={})
    assert not serializer.is_valid()
    assert "original_url" in serializer.errors


def test_create_serializer_blank_url_is_invalid() -> None:
    serializer = URLCreateSerializer(data={"original_url": ""})
    assert not serializer.is_valid()
    assert "original_url" in serializer.errors


@pytest.mark.parametrize(
    "bad_url",
    ["not-a-url", "just some text", "http://"],
)
def test_create_serializer_rejects_invalid_urls(bad_url: str) -> None:
    serializer = URLCreateSerializer(data={"original_url": bad_url})
    assert not serializer.is_valid(), f"Expected invalid for: {bad_url!r}"


# ---------------------------------------------------------------------------
# URLCreateSerializer — creation (Mod 5, unchanged)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_serializer_saves_url_to_db() -> None:
    serializer = URLCreateSerializer(data={"original_url": "https://www.example.com"})
    assert serializer.is_valid()
    url = serializer.save()
    assert URL.objects.filter(pk=url.pk).exists()


@pytest.mark.django_db
def test_create_serializer_assigns_short_code() -> None:
    serializer = URLCreateSerializer(data={"original_url": "https://www.example.com"})
    assert serializer.is_valid()
    url = serializer.save()
    assert url.short_code
    assert len(url.short_code) == 6


@pytest.mark.django_db
def test_create_serializer_stores_correct_original_url() -> None:
    original = "https://www.example.com/path?q=1"
    serializer = URLCreateSerializer(data={"original_url": original})
    assert serializer.is_valid()
    url = serializer.save()
    assert url.original_url == original


# ---------------------------------------------------------------------------
# URLCreateSerializer — Mod 6 tag support
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_serializer_accepts_tags(tag_marketing: Tag, tag_social: Tag) -> None:
    serializer = URLCreateSerializer(
        data={
            "original_url": "https://example.com",
            "tags": ["Marketing", "Social"],
        }
    )
    assert serializer.is_valid(), serializer.errors
    url = serializer.save()
    tag_names = set(url.tags.values_list("name", flat=True))
    assert tag_names == {"Marketing", "Social"}


@pytest.mark.django_db
def test_create_serializer_rejects_nonexistent_tag() -> None:
    serializer = URLCreateSerializer(
        data={
            "original_url": "https://example.com",
            "tags": ["DoesNotExist"],
        }
    )
    assert not serializer.is_valid()
    assert "tags" in serializer.errors


@pytest.mark.django_db
def test_create_serializer_no_tags_is_valid() -> None:
    serializer = URLCreateSerializer(data={"original_url": "https://example.com"})
    assert serializer.is_valid(), serializer.errors
    url = serializer.save()
    assert url.tags.count() == 0


# ---------------------------------------------------------------------------
# URLResponseSerializer — output shape (Mod 5 + Mod 6 fields)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_response_serializer_contains_expected_fields(created_url: URL) -> None:
    serializer = URLResponseSerializer(created_url)
    data = serializer.data
    expected = {
        "short_code", "original_url", "short_url", "custom_alias",
        "tags", "click_count", "is_active", "is_expired",
        "expires_at", "title", "description", "favicon", "created_at",
    }
    assert set(data.keys()) == expected


@pytest.mark.django_db
def test_response_serializer_short_url_without_request(created_url: URL) -> None:
    serializer = URLResponseSerializer(created_url)
    assert serializer.data["short_url"] == f"/{created_url.short_code}/"


@pytest.mark.django_db
def test_response_serializer_short_url_with_request(created_url: URL) -> None:
    factory = APIRequestFactory()
    request = factory.get("/")
    serializer = URLResponseSerializer(created_url, context={"request": request})
    short_url = serializer.data["short_url"]
    assert short_url.startswith("http")
    assert created_url.short_code in short_url


@pytest.mark.django_db
def test_response_serializer_tags_are_serialized(
    created_url: URL, tag_marketing: Tag
) -> None:
    created_url.tags.add(tag_marketing)
    serializer = URLResponseSerializer(created_url)
    tag_names = [t["name"] for t in serializer.data["tags"]]
    assert "Marketing" in tag_names


@pytest.mark.django_db
def test_response_serializer_click_count_is_zero_by_default(created_url: URL) -> None:
    serializer = URLResponseSerializer(created_url)
    assert serializer.data["click_count"] == 0


@pytest.mark.django_db
def test_response_serializer_is_expired_false(created_url: URL) -> None:
    serializer = URLResponseSerializer(created_url)
    assert serializer.data["is_expired"] is False


# ---------------------------------------------------------------------------
# URLAnalyticsSerializer (Mod 6)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_analytics_serializer_contains_expected_fields(created_url: URL) -> None:
    serializer = URLAnalyticsSerializer(created_url)
    assert "clicks_by_country" in serializer.data
    assert "recent_clicks" in serializer.data
    assert "click_count" in serializer.data


@pytest.mark.django_db
def test_analytics_serializer_clicks_by_country(created_url: URL) -> None:
    Click.objects.create(url=created_url, ip_address="1.1.1.1", user_agent="ua", country="RW")
    Click.objects.create(url=created_url, ip_address="2.2.2.2", user_agent="ua", country="RW")
    Click.objects.create(url=created_url, ip_address="3.3.3.3", user_agent="ua", country="US")

    serializer = URLAnalyticsSerializer(created_url)
    by_country = {row["country"]: row["total"] for row in serializer.data["clicks_by_country"]}
    assert by_country["RW"] == 2
    assert by_country["US"] == 1


@pytest.mark.django_db
def test_analytics_serializer_recent_clicks_list(created_url: URL) -> None:
    Click.objects.create(url=created_url, ip_address="1.1.1.1", user_agent="ua")
    serializer = URLAnalyticsSerializer(created_url)
    assert len(serializer.data["recent_clicks"]) == 1
    assert serializer.data["recent_clicks"][0]["ip_address"] == "1.1.1.1"
