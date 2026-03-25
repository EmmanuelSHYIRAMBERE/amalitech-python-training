"""Shared pytest fixtures for the weather service test suite."""

import pytest
from weather.mock_provider import MockWeatherProvider
from weather.service import WeatherService

VALID_KEY = "valid-key-123"


@pytest.fixture(scope="session")
def valid_api_key() -> str:
    """Return the shared valid API key used across tests."""
    return VALID_KEY


@pytest.fixture
def mock_provider(valid_api_key: str) -> MockWeatherProvider:
    """Return a fresh MockWeatherProvider for each test."""
    return MockWeatherProvider(valid_api_key=valid_api_key)


@pytest.fixture
def weather_service(
    mock_provider: MockWeatherProvider, valid_api_key: str
) -> WeatherService:
    """Return a WeatherService backed by MockWeatherProvider."""
    return WeatherService(provider=mock_provider, api_key=valid_api_key)
