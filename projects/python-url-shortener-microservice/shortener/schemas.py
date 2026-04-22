"""Value objects and typed response shapes for the shortener app.

Dataclasses decouple the service logic from DRF serializer internals:
  ShortenRequest  — input to the shortening operation
  ShortenResult   — output of the shortening operation

TypedDicts provide a typed schema for JSON response dicts:
  URLResponseDict — shape of the POST /api/v1/urls/ response body
  HealthResponseDict — shape of the GET /health/ response body
"""

from dataclasses import dataclass
from typing import TypedDict


# ---------------------------------------------------------------------------
# Dataclasses — typed value objects (mirrors WeatherRequest / WeatherResponse)
# ---------------------------------------------------------------------------


@dataclass
class ShortenRequest:
    """Encapsulates the input for a URL shortening operation.

    Attributes:
        original_url: The full URL to be shortened.
    """

    original_url: str


@dataclass
class ShortenResult:
    """Encapsulates the output of a URL shortening operation.

    Attributes:
        short_code: The generated short identifier.
        original_url: The original URL that was shortened.
        short_url: The fully-qualified short URL (absolute URI).
        created_at: ISO-8601 timestamp of when the record was created.
    """

    short_code: str
    original_url: str
    short_url: str
    created_at: str


# ---------------------------------------------------------------------------
# TypedDicts — typed shapes for JSON response bodies
# (mirrors ReportDict(TypedDict) from the grade analytics lab)
# ---------------------------------------------------------------------------


class URLResponseDict(TypedDict):
    """Typed schema for the POST /api/v1/urls/ JSON response body."""

    short_code: str
    original_url: str
    short_url: str
    created_at: str


class HealthResponseDict(TypedDict):
    """Typed schema for the GET /health/ JSON response body."""

    status: str
    db: str
