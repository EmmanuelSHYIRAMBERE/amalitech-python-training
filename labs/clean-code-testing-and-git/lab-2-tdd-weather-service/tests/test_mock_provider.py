"""Tests for the abstract WeatherProvider interface and MockWeatherProvider."""

import pytest

from weather.exceptions import CityNotFoundError, InvalidAPIKeyError
from weather.mock_provider import MockWeatherProvider
from weather.models import WeatherRequest, WeatherResponse


VALID_KEY = "valid-key-123"
KNOWN_CITIES = ["Accra", "Berlin", "Tokyo", "New York", "Lagos"]


@pytest.fixture
def provider() -> MockWeatherProvider:
    """Return a MockWeatherProvider with a valid API key."""
    return MockWeatherProvider(valid_api_key=VALID_KEY)


def test_provider_returns_weather_response(provider: MockWeatherProvider) -> None:
    req = WeatherRequest(city="Accra", api_key=VALID_KEY)
    result = provider.fetch(req)
    assert isinstance(result, WeatherResponse)


@pytest.mark.parametrize("city", KNOWN_CITIES)
def test_provider_knows_all_known_cities(provider: MockWeatherProvider, city: str) -> None:
    req = WeatherRequest(city=city, api_key=VALID_KEY)
    result = provider.fetch(req)
    assert result.city == city


def test_provider_raises_city_not_found(provider: MockWeatherProvider) -> None:
    req = WeatherRequest(city="Atlantis", api_key=VALID_KEY)
    with pytest.raises(CityNotFoundError):
        provider.fetch(req)


def test_provider_raises_invalid_api_key(provider: MockWeatherProvider) -> None:
    req = WeatherRequest(city="Accra", api_key="wrong-key")
    with pytest.raises(InvalidAPIKeyError):
        provider.fetch(req)


def test_provider_response_has_valid_humidity(provider: MockWeatherProvider) -> None:
    req = WeatherRequest(city="Berlin", api_key=VALID_KEY)
    result = provider.fetch(req)
    assert 0 <= result.humidity_pct <= 100


def test_provider_response_has_condition_string(provider: MockWeatherProvider) -> None:
    req = WeatherRequest(city="Tokyo", api_key=VALID_KEY)
    result = provider.fetch(req)
    assert isinstance(result.condition, str)
    assert len(result.condition) > 0
