"""Value objects and typed response shapes for the shortener app — Module 6.

Dataclass patterns applied from the labs:

  Clean Code Lab 2 (WeatherRequest / WeatherResponse):
    - @dataclass for typed request/response value objects
    - Strict type hints on every field

  Python Advanced Lab 1 (Grade / Student):
    - Business methods on dataclasses (Grade.letter(), Student.gpa())
    - field(default_factory=...) for mutable defaults
    - __post_init__ for validation (mirrors Student property setters)

  Additional best practice:
    - frozen=True on output/result dataclasses — they are immutable value
      objects; once created they must not be mutated.

Dataclasses:
  ShortenRequest  — input to the shortening operation (validated)
  ShortenResult   — immutable output of the shortening operation
  ClickResult     — immutable typed representation of a logged click

TypedDicts:
  URLResponseDict    — shape of the POST /api/v1/urls/ response body
  HealthResponseDict — shape of the GET /health/ response body
"""

from dataclasses import dataclass, field
from typing import TypedDict

# ---------------------------------------------------------------------------
# Dataclasses — typed value objects
# ---------------------------------------------------------------------------


@dataclass
class ShortenRequest:
    """Encapsulates and validates the input for a URL shortening operation.

    Mirrors the WeatherRequest dataclass from Clean Code Lab 2 and adds
    __post_init__ validation, mirroring the @property setter pattern from
    Python Basics Lab 1 (Student.name setter raises ValueError on bad input).

    Attributes:
        original_url: The full URL to be shortened. Must be non-empty.

    Raises:
        ValueError: If ``original_url`` is empty or whitespace-only.

    Example::

        req = ShortenRequest(original_url="https://example.com")
        # ShortenRequest(original_url='https://example.com')
    """

    original_url: str

    def __post_init__(self) -> None:
        """Validate fields immediately after construction.

        Raises:
            ValueError: If ``original_url`` is empty or whitespace-only.
        """
        if not self.original_url or not self.original_url.strip():
            raise ValueError("original_url must be a non-empty string.")


@dataclass(frozen=True)
class ShortenResult:
    """Immutable output of a URL shortening operation.

    ``frozen=True`` makes every field read-only after construction —
    a ShortenResult is a value object that should never be mutated.
    Mirrors the WeatherResponse dataclass from Clean Code Lab 2.

    Attributes:
        short_code: The generated short identifier (e.g. 'aB3xYz').
        original_url: The original URL that was shortened.
        short_url: The fully-qualified short URL (absolute URI).
        created_at: ISO-8601 timestamp of when the record was created.

    Example::

        result = ShortenResult(
            short_code="aB3xYz",
            original_url="https://example.com",
            short_url="http://localhost/aB3xYz/",
            created_at="2025-01-01T00:00:00Z",
        )
        result.short_code = "other"  # raises FrozenInstanceError
    """

    short_code: str
    original_url: str
    short_url: str
    created_at: str

    def as_dict(self) -> dict[str, str]:
        """Return a plain dict representation of this result.

        Mirrors the Grade.letter() pattern from Python Advanced Lab 1 —
        a business method on a dataclass that derives a useful value.

        Returns:
            Dict with keys: short_code, original_url, short_url, created_at.
        """
        return {
            "short_code": self.short_code,
            "original_url": self.original_url,
            "short_url": self.short_url,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class ClickResult:
    """Immutable typed representation of a single logged click event.

    ``frozen=True`` makes this a true value object — click records are
    append-only analytics data and must never be mutated after creation.

    Required fields come first; optional fields use ``field(default=None)``
    to mirror the ``field(default_factory=list)`` pattern from Python
    Advanced Lab 1 (Student.grades).

    Attributes:
        url_id: PK of the URL that was clicked.
        ip_address: Client IP address (IPv4 or IPv6).
        user_agent: Browser / OS string from the HTTP User-Agent header.
        country: ISO 3166-1 alpha-2 country code (nullable).
        city: Geo-resolved city name (nullable).
        referrer: HTTP Referer header value (nullable).

    Example::

        click = ClickResult(url_id=1, ip_address="1.2.3.4", user_agent="Mozilla/5.0")
        click.country = "RW"  # raises FrozenInstanceError
    """

    url_id: int
    ip_address: str
    user_agent: str
    country: str | None = field(default=None)
    city: str | None = field(default=None)
    referrer: str | None = field(default=None)

    def has_geo(self) -> bool:
        """Return True if geo-location data is available for this click.

        Mirrors the Grade.letter() pattern from Python Advanced Lab 1 —
        a business method that derives a meaningful boolean from the data.

        Returns:
            ``True`` if both country and city are set, ``False`` otherwise.

        Example::

            click = ClickResult(url_id=1, ip_address="1.2.3.4",
                                user_agent="ua", country="RW", city="Kigali")
            assert click.has_geo() is True
        """
        return self.country is not None and self.city is not None

    def is_known_referrer(self) -> bool:
        """Return True if the click came from a tracked referrer.

        Returns:
            ``True`` if referrer is set and non-empty, ``False`` otherwise.
        """
        return bool(self.referrer)


# ---------------------------------------------------------------------------
# TypedDicts — typed shapes for JSON response bodies
# (mirrors ReportDict(TypedDict) from Python Advanced Lab 1)
# ---------------------------------------------------------------------------


class URLResponseDict(TypedDict):
    """Typed schema for the POST /api/v1/urls/ JSON response body.

    mypy verifies that any dict annotated as URLResponseDict has exactly
    these keys with these value types — typos are caught at type-check time.
    """

    short_code: str
    original_url: str
    short_url: str
    created_at: str


class HealthResponseDict(TypedDict):
    """Typed schema for the GET /health/ JSON response body."""

    status: str
    db: str
