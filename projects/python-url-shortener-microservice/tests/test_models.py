"""Tests for shortener.models — URL model and generate_short_code."""

import string
from unittest.mock import patch

import pytest

from shortener.models import URL, generate_short_code


# ---------------------------------------------------------------------------
# generate_short_code
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_generate_short_code_returns_string() -> None:
    """generate_short_code must return a str."""
    code = generate_short_code()
    assert isinstance(code, str)


@pytest.mark.django_db
def test_generate_short_code_default_length() -> None:
    """Default length must be 6 characters."""
    code = generate_short_code()
    assert len(code) == 6


@pytest.mark.django_db
def test_generate_short_code_custom_length() -> None:
    """Custom length argument must be respected."""
    code = generate_short_code(length=10)
    assert len(code) == 10


@pytest.mark.django_db
def test_generate_short_code_only_alphanumeric_chars() -> None:
    """Generated code must contain only ASCII letters and digits."""
    allowed = set(string.ascii_letters + string.digits)
    for _ in range(20):
        code = generate_short_code()
        assert set(code).issubset(allowed), f"Non-alphanumeric chars in: {code!r}"


@pytest.mark.django_db
def test_generate_short_code_is_unique_when_collision_occurs() -> None:
    """generate_short_code must retry until it finds a code not in the DB."""
    URL.objects.create(original_url="https://example.com", short_code="aaaaaa")

    # Force the first call to return the existing code, second call returns a new one.
    with patch(
        "shortener.models.random.choices",
        side_effect=[list("aaaaaa"), list("bbbbbb")],
    ):
        code = generate_short_code()

    assert code == "bbbbbb"


@pytest.mark.django_db
def test_generate_short_code_produces_different_codes_on_successive_calls() -> None:
    """Two successive calls should (almost certainly) return different codes."""
    codes = {generate_short_code() for _ in range(10)}
    # With 62^6 ≈ 56 billion possibilities, all 10 must be unique.
    assert len(codes) == 10


# ---------------------------------------------------------------------------
# URL model
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_url_str_contains_short_code_and_original_url(created_url: URL) -> None:
    """__str__ must include both the short_code and the original_url."""
    result = str(created_url)
    assert created_url.short_code in result
    assert created_url.original_url in result


@pytest.mark.django_db
def test_url_str_format(created_url: URL) -> None:
    """__str__ must use the arrow separator defined in the model."""
    assert str(created_url) == f"{created_url.short_code} → {created_url.original_url}"


@pytest.mark.django_db
def test_url_created_at_is_set_on_save(created_url: URL) -> None:
    """created_at must be populated automatically by TimeStampedModel."""
    assert created_url.created_at is not None


@pytest.mark.django_db
def test_url_updated_at_is_set_on_save(created_url: URL) -> None:
    """updated_at must be populated automatically by TimeStampedModel."""
    assert created_url.updated_at is not None


@pytest.mark.django_db
def test_url_short_code_is_unique() -> None:
    """Creating two URLs with the same short_code must raise an IntegrityError."""
    from django.db import IntegrityError

    URL.objects.create(original_url="https://first.com", short_code="unique1")
    with pytest.raises(IntegrityError):
        URL.objects.create(original_url="https://second.com", short_code="unique1")


@pytest.mark.django_db
def test_url_ordering_is_newest_first() -> None:
    """Default queryset ordering must be descending by created_at."""
    URL.objects.create(original_url="https://first.com", short_code="first1")
    URL.objects.create(original_url="https://second.com", short_code="secnd1")
    urls = list(URL.objects.all())
    assert urls[0].short_code == "secnd1"
    assert urls[1].short_code == "first1"
