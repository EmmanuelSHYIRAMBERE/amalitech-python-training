"""Tests for shortener models, generators, validators, schemas, and protocols."""

import string

import pytest

from shortener.generators import BaseShortCodeGenerator, default_generator
from shortener.models import URL
from shortener.protocols import ShortCodeGenerator
from shortener.schemas import ShortenRequest, ShortenResult
from shortener.validators import validate_short_code, validate_url_scheme

# ---------------------------------------------------------------------------
# SecureShortCodeGenerator
# ---------------------------------------------------------------------------


def test_generator_returns_string() -> None:
    """generate() must return a str."""
    assert isinstance(default_generator.generate(), str)


def test_generator_default_length() -> None:
    """Default length must be 6 characters."""
    assert len(default_generator.generate()) == 6


def test_generator_custom_length() -> None:
    """Custom length argument must be respected."""
    assert len(default_generator.generate(length=10)) == 10


def test_generator_only_alphanumeric_chars() -> None:
    """Generated code must contain only ASCII letters and digits."""
    allowed = set(string.ascii_letters + string.digits)
    for _ in range(20):
        code = default_generator.generate()
        assert set(code).issubset(allowed), f"Non-alphanumeric chars in: {code!r}"


def test_generator_produces_different_codes_on_successive_calls() -> None:
    """Ten successive calls should all produce unique codes."""
    codes = {default_generator.generate() for _ in range(10)}
    assert len(codes) == 10


def test_generator_callable_interface() -> None:
    """Calling the instance directly (Protocol __call__) must work."""
    code = default_generator(length=6)
    assert isinstance(code, str)
    assert len(code) == 6


# ---------------------------------------------------------------------------
# Protocol and ABC structural checks
# ---------------------------------------------------------------------------


def test_secure_generator_is_instance_of_abc() -> None:
    """SecureShortCodeGenerator must be a subclass of BaseShortCodeGenerator."""
    assert isinstance(default_generator, BaseShortCodeGenerator)


def test_secure_generator_satisfies_protocol() -> None:
    """SecureShortCodeGenerator must satisfy the ShortCodeGenerator Protocol."""
    assert isinstance(default_generator, ShortCodeGenerator)


def test_plain_function_satisfies_protocol() -> None:
    """Any callable with the right signature satisfies ShortCodeGenerator Protocol."""

    def my_gen(length: int = 6) -> str:
        return "x" * length

    assert isinstance(my_gen, ShortCodeGenerator)


def test_base_generator_cannot_be_instantiated() -> None:
    """BaseShortCodeGenerator is abstract and must not be instantiatable directly."""
    with pytest.raises(TypeError):
        BaseShortCodeGenerator()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Validators (regex)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", ["abc123", "aB3xYz", "abcd", "abcdefghij"])
def test_validate_short_code_accepts_valid(code: str) -> None:
    assert validate_short_code(code) is True


@pytest.mark.parametrize(
    "code", ["ab", "../admin", "<script>", "abc 123", "abc-123!", ""]
)
def test_validate_short_code_rejects_invalid(code: str) -> None:
    assert validate_short_code(code) is False


@pytest.mark.parametrize("url", ["https://example.com", "http://example.com/path?q=1"])
def test_validate_url_scheme_accepts_http_https(url: str) -> None:
    assert validate_url_scheme(url) is True


@pytest.mark.parametrize("url", ["ftp://example.com", "not-a-url", "", "http://"])
def test_validate_url_scheme_rejects_non_http(url: str) -> None:
    assert validate_url_scheme(url) is False


# ---------------------------------------------------------------------------
# Dataclasses (schemas)
# ---------------------------------------------------------------------------


def test_shorten_request_stores_url() -> None:
    req = ShortenRequest(original_url="https://example.com")
    assert req.original_url == "https://example.com"


def test_shorten_result_stores_all_fields() -> None:
    result = ShortenResult(
        short_code="abc123",
        original_url="https://example.com",
        short_url="http://localhost/abc123/",
        created_at="2025-01-01T00:00:00Z",
    )
    assert result.short_code == "abc123"
    assert result.original_url == "https://example.com"
    assert result.short_url == "http://localhost/abc123/"
    assert result.created_at == "2025-01-01T00:00:00Z"


def test_shorten_request_repr_contains_url() -> None:
    req = ShortenRequest(original_url="https://example.com")
    assert "https://example.com" in repr(req)


# ---------------------------------------------------------------------------
# URL model
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_url_str_format(created_url: URL) -> None:
    """__str__ must use the arrow separator defined in the model."""
    assert str(created_url) == f"{created_url.short_code} → {created_url.original_url}"


@pytest.mark.django_db
def test_url_created_at_is_set_on_save(created_url: URL) -> None:
    assert created_url.created_at is not None


@pytest.mark.django_db
def test_url_updated_at_is_set_on_save(created_url: URL) -> None:
    assert created_url.updated_at is not None


@pytest.mark.django_db
def test_url_short_code_is_unique() -> None:
    from django.db import IntegrityError

    URL.objects.create(original_url="https://first.com", short_code="unique1")
    with pytest.raises(IntegrityError):
        URL.objects.create(original_url="https://second.com", short_code="unique1")


@pytest.mark.django_db
def test_url_ordering_is_newest_first() -> None:
    URL.objects.create(original_url="https://first.com", short_code="first1")
    URL.objects.create(original_url="https://second.com", short_code="secnd1")
    urls = list(URL.objects.all())
    assert urls[0].short_code == "secnd1"
    assert urls[1].short_code == "first1"
