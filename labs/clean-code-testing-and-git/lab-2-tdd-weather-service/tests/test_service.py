"""Tests for WeatherService — the main public-facing service class."""

import logging

import pytest
from pytest_mock import MockerFixture

from weather.exceptions import CityNotFoundError, InvalidAPIKeyError
from weather.mock_provider import MockWeatherProvider
from weather.models import WeatherResponse
from weather.service import WeatherService


VALID_KEY = "valid-key-123"


@pytest.fixture
def service() -> WeatherService:
    """Return a WeatherService backed by MockWeatherProvider."""
    provider = MockWeatherProvider(valid_api_key=VALID_KEY)
    return WeatherService(provider=provider, api_key=VALID_KEY)


# --- Happy path ---

def test_get_forecast_returns_weather_response(service: WeatherService) -> None:
    result = service.get_forecast("Accra")
    assert isinstance(result, WeatherResponse)


def test_get_forecast_correct_city(service: WeatherService) -> None:
    result = service.get_forecast("Berlin")
    assert result.city == "Berlin"


def test_get_forecast_correct_temperature(service: WeatherService) -> None:
    result = service.get_forecast("Tokyo")
    assert result.temperature_c == 22.0


@pytest.mark.parametrize("city,expected_condition", [
    ("Accra", "Sunny"),
    ("Berlin", "Cloudy"),
    ("Lagos", "Humid"),
])
def test_get_forecast_conditions(service: WeatherService, city: str, expected_condition: str) -> None:
    result = service.get_forecast(city)
    assert result.condition == expected_condition


# --- Error handling ---

def test_get_forecast_unknown_city_raises(service: WeatherService) -> None:
    with pytest.raises(CityNotFoundError):
        service.get_forecast("Atlantis")


def test_get_forecast_invalid_key_raises() -> None:
    provider = MockWeatherProvider(valid_api_key=VALID_KEY)
    bad_service = WeatherService(provider=provider, api_key="wrong")
    with pytest.raises(InvalidAPIKeyError):
        bad_service.get_forecast("Accra")


def test_get_forecast_empty_city_raises(service: WeatherService) -> None:
    with pytest.raises(ValueError, match="city"):
        service.get_forecast("")


def test_get_forecast_whitespace_city_raises(service: WeatherService) -> None:
    with pytest.raises(ValueError, match="city"):
        service.get_forecast("   ")


# --- Logging ---

def test_get_forecast_logs_request(service: WeatherService, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="weather.service"):
        service.get_forecast("Accra")
    assert "Accra" in caplog.text


def test_get_forecast_logs_error_on_city_not_found(
    service: WeatherService, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="weather.service"):
        with pytest.raises(CityNotFoundError):
            service.get_forecast("Atlantis")
    assert "Atlantis" in caplog.text


# --- Dependency injection / mocking ---

def test_service_delegates_to_provider(mocker: MockerFixture) -> None:
    mock_provider = mocker.MagicMock()
    mock_provider.fetch.return_value = WeatherResponse(
        city="Accra", temperature_c=32.0, condition="Sunny", humidity_pct=60
    )
    svc = WeatherService(provider=mock_provider, api_key=VALID_KEY)
    svc.get_forecast("Accra")
    mock_provider.fetch.assert_called_once()


def test_service_passes_correct_request_to_provider(mocker: MockerFixture) -> None:
    mock_provider = mocker.MagicMock()
    mock_provider.fetch.return_value = WeatherResponse(
        city="Lagos", temperature_c=30.0, condition="Humid", humidity_pct=85
    )
    svc = WeatherService(provider=mock_provider, api_key=VALID_KEY)
    svc.get_forecast("Lagos")
    call_args = mock_provider.fetch.call_args[0][0]
    assert call_args.city == "Lagos"
    assert call_args.api_key == VALID_KEY
