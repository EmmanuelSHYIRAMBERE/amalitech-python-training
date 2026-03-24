"""Abstract WeatherProvider interface (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod

from weather.models import WeatherRequest, WeatherResponse


class WeatherProvider(ABC):
    """Abstract base class defining the contract for weather data providers.

    Any concrete provider (mock, OpenWeatherMap, etc.) must implement
    the ``fetch`` method, allowing WeatherService to remain decoupled
    from the underlying data source.
    """

    @abstractmethod
    def fetch(self, request: WeatherRequest) -> WeatherResponse:
        """Fetch a weather forecast for the given request.

        Args:
            request: A WeatherRequest containing city and API key.

        Returns:
            A WeatherResponse with forecast data.

        Raises:
            InvalidAPIKeyError: If the API key is not valid.
            CityNotFoundError: If the city cannot be resolved.
        """
