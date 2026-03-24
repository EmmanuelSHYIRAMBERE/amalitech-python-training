"""Tests for WeatherRequest and WeatherResponse dataclasses."""

from weather.models import WeatherRequest, WeatherResponse


def test_weather_request_stores_city() -> None:
    req = WeatherRequest(city="Accra", api_key="test-key")
    assert req.city == "Accra"
    assert req.api_key == "test-key"


def test_weather_response_stores_forecast() -> None:
    resp = WeatherResponse(
        city="Accra",
        temperature_c=32.0,
        condition="Sunny",
        humidity_pct=60,
    )
    assert resp.city == "Accra"
    assert resp.temperature_c == 32.0
    assert resp.condition == "Sunny"
    assert resp.humidity_pct == 60


def test_weather_response_repr_contains_city() -> None:
    resp = WeatherResponse(
        city="Accra", temperature_c=32.0, condition="Sunny", humidity_pct=60
    )
    assert "Accra" in repr(resp)
