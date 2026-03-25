"""WeatherService — the main public-facing service class."""

import logging

from weather.exceptions import CityNotFoundError, InvalidAPIKeyError
from weather.models import WeatherRequest, WeatherResponse
from weather.provider import WeatherProvider

logger = logging.getLogger(__name__)


class WeatherService:
    """High-level service for retrieving weather forecasts.

    Depends on an abstract WeatherProvider, making it easy to swap
    the mock provider for a real one without changing this class
    (Open/Closed Principle).

    Args:
        provider: Any concrete WeatherProvider implementation.
        api_key: The API key forwarded to the provider on each request.

    Example:
        >>> provider = MockWeatherProvider(valid_api_key="my-key")
        >>> service = WeatherService(provider=provider, api_key="my-key")
        >>> forecast = service.get_forecast("Accra")
        >>> print(forecast.temperature_c)
        32.0
    """

    def __init__(self, provider: WeatherProvider, api_key: str) -> None:
        self._provider = provider
        self._api_key = api_key

    def get_forecast(self, city: str) -> WeatherResponse:
        """Return a weather forecast for the given city.

        Args:
            city: The name of the city to query. Must be non-empty.

        Returns:
            A WeatherResponse containing temperature, condition, and humidity.

        Raises:
            ValueError: If ``city`` is empty or whitespace.
            InvalidAPIKeyError: If the configured API key is rejected.
            CityNotFoundError: If the city is unknown to the provider.
        """
        if not city or not city.strip():
            raise ValueError("city must be a non-empty string")

        logger.info("Fetching forecast for city=%r", city)
        request = WeatherRequest(city=city, api_key=self._api_key)

        try:
            response = self._provider.fetch(request)
        except (InvalidAPIKeyError, CityNotFoundError) as exc:
            logger.warning("Forecast request failed: %s", exc)
            raise

        logger.info(
            "Forecast retrieved: city=%r temp=%.1f°C",
            response.city,
            response.temperature_c,
        )
        return response
