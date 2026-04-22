"""Tests for shortener.serializers — URLCreateSerializer and URLResponseSerializer."""

import pytest
from rest_framework.test import APIRequestFactory

from shortener.models import URL
from shortener.serializers import URLCreateSerializer, URLResponseSerializer

# ---------------------------------------------------------------------------
# URLCreateSerializer — validation
# ---------------------------------------------------------------------------


def test_create_serializer_valid_url_is_valid() -> None:
    """A well-formed URL must pass serializer validation."""
    serializer = URLCreateSerializer(data={"original_url": "https://www.example.com"})
    assert serializer.is_valid(), serializer.errors


def test_create_serializer_missing_url_is_invalid() -> None:
    """An empty payload must fail validation."""
    serializer = URLCreateSerializer(data={})
    assert not serializer.is_valid()
    assert "original_url" in serializer.errors


def test_create_serializer_blank_url_is_invalid() -> None:
    """A blank string must fail validation."""
    serializer = URLCreateSerializer(data={"original_url": ""})
    assert not serializer.is_valid()
    assert "original_url" in serializer.errors


@pytest.mark.parametrize(
    "bad_url",
    [
        "not-a-url",
        "just some text",
        "http://",
        # Note: Django's URLField accepts any scheme (ftp://, etc.) by design.
    ],
)
def test_create_serializer_rejects_invalid_urls(bad_url: str) -> None:
    """Structurally malformed URLs must be rejected by the serializer."""
    serializer = URLCreateSerializer(data={"original_url": bad_url})
    assert not serializer.is_valid(), f"Expected invalid for: {bad_url!r}"


# ---------------------------------------------------------------------------
# URLCreateSerializer — creation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_serializer_saves_url_to_db() -> None:
    """A valid serializer.save() must persist a URL record."""
    serializer = URLCreateSerializer(data={"original_url": "https://www.example.com"})
    assert serializer.is_valid()
    url = serializer.save()
    assert URL.objects.filter(pk=url.pk).exists()


@pytest.mark.django_db
def test_create_serializer_assigns_short_code() -> None:
    """The saved URL must have a non-empty short_code."""
    serializer = URLCreateSerializer(data={"original_url": "https://www.example.com"})
    assert serializer.is_valid()
    url = serializer.save()
    assert url.short_code
    assert len(url.short_code) == 6


@pytest.mark.django_db
def test_create_serializer_stores_correct_original_url() -> None:
    """The saved URL must preserve the original_url exactly."""
    original = "https://www.example.com/path?q=1"
    serializer = URLCreateSerializer(data={"original_url": original})
    assert serializer.is_valid()
    url = serializer.save()
    assert url.original_url == original


# ---------------------------------------------------------------------------
# URLResponseSerializer — output shape
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_response_serializer_contains_expected_fields(created_url: URL) -> None:
    """Response serializer must expose short_code, original_url, short_url, created_at."""
    serializer = URLResponseSerializer(created_url)
    data = serializer.data
    assert set(data.keys()) == {"short_code", "original_url", "short_url", "created_at"}


@pytest.mark.django_db
def test_response_serializer_short_url_without_request(created_url: URL) -> None:
    """Without a request context, short_url must fall back to /<short_code>/."""
    serializer = URLResponseSerializer(created_url)
    assert serializer.data["short_url"] == f"/{created_url.short_code}/"


@pytest.mark.django_db
def test_response_serializer_short_url_with_request(created_url: URL) -> None:
    """With a request context, short_url must be an absolute URI."""
    factory = APIRequestFactory()
    request = factory.get("/")
    serializer = URLResponseSerializer(created_url, context={"request": request})
    short_url = serializer.data["short_url"]
    assert short_url.startswith("http")
    assert created_url.short_code in short_url


@pytest.mark.django_db
def test_response_serializer_short_code_matches_model(created_url: URL) -> None:
    """short_code in response must match the model's short_code."""
    serializer = URLResponseSerializer(created_url)
    assert serializer.data["short_code"] == created_url.short_code


@pytest.mark.django_db
def test_response_serializer_original_url_matches_model(created_url: URL) -> None:
    """original_url in response must match the model's original_url."""
    serializer = URLResponseSerializer(created_url)
    assert serializer.data["original_url"] == created_url.original_url
