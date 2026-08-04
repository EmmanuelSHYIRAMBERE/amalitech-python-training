"""Custom exceptions for the Weather service."""


class WeatherServiceError(Exception):
    """Base exception for all Weather service errors."""


class InvalidAPIKeyError(WeatherServiceError):
    """Raised when the provided API key is invalid or missing.

    Args:
        key: The invalid API key that was provided.
    """

    def __init__(self, key: str) -> None:
        super().__init__(f"Invalid API key: '{key}'")


class CityNotFoundError(WeatherServiceError):
    """Raised when the requested city is not found in the provider.

    Args:
        city: The city name that could not be resolved.
    """

    def __init__(self, city: str) -> None:
        super().__init__(f"City not found: '{city}'")
