"""Mock implementation of WeatherProvider returning predefined data."""

from weather.exceptions import CityNotFoundError, InvalidAPIKeyError
from weather.models import WeatherRequest, WeatherResponse
from weather.provider import WeatherProvider

_MOCK_DATA: dict[str, WeatherResponse] = {
    "Accra": WeatherResponse(
        city="Accra", temperature_c=32.0, condition="Sunny", humidity_pct=60
    ),
    "Berlin": WeatherResponse(
        city="Berlin", temperature_c=14.0, condition="Cloudy", humidity_pct=72
    ),
    "Tokyo": WeatherResponse(
        city="Tokyo", temperature_c=22.0, condition="Partly Cloudy", humidity_pct=65
    ),
    "New York": WeatherResponse(
        city="New York", temperature_c=18.0, condition="Windy", humidity_pct=55
    ),
    "Lagos": WeatherResponse(
        city="Lagos", temperature_c=30.0, condition="Humid", humidity_pct=85
    ),
}


class MockWeatherProvider(WeatherProvider):
    """Simulates a weather data provider with hardcoded responses.

    Designed for testing and development. Returns deterministic data
    for a fixed set of known cities and raises appropriate exceptions
    for invalid inputs.

    Args:
        valid_api_key: The only API key this mock will accept.
    """

    def __init__(self, valid_api_key: str) -> None:
        self._valid_api_key = valid_api_key

    def fetch(self, request: WeatherRequest) -> WeatherResponse:
        """Return mock forecast data for a known city.

        Args:
            request: The weather request containing city and API key.

        Returns:
            A predefined WeatherResponse for the requested city.

        Raises:
            InvalidAPIKeyError: If ``request.api_key`` does not match the valid key.
            CityNotFoundError: If ``request.city`` is not in the known cities set.
        """
        if request.api_key != self._valid_api_key:
            raise InvalidAPIKeyError(request.api_key)
        if request.city not in _MOCK_DATA:
            raise CityNotFoundError(request.city)
        return _MOCK_DATA[request.city]
