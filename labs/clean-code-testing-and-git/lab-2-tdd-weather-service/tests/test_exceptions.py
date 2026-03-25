"""Tests for custom Weather service exceptions."""

import pytest
from weather.exceptions import (
    CityNotFoundError,
    InvalidAPIKeyError,
    WeatherServiceError,
)


def test_invalid_api_key_error_is_weather_service_error() -> None:
    with pytest.raises(WeatherServiceError):
        raise InvalidAPIKeyError("bad-key")


def test_city_not_found_error_is_weather_service_error() -> None:
    with pytest.raises(WeatherServiceError):
        raise CityNotFoundError("Atlantis")


def test_invalid_api_key_error_message() -> None:
    exc = InvalidAPIKeyError("bad-key")
    assert "bad-key" in str(exc)


def test_city_not_found_error_message() -> None:
    exc = CityNotFoundError("Atlantis")
    assert "Atlantis" in str(exc)
