"""Dataclasses for Weather API request parameters and response models."""

from dataclasses import dataclass


@dataclass
class WeatherRequest:
    """Encapsulates parameters for a weather forecast request.

    Attributes:
        city: The name of the city to query.
        api_key: The API key used to authenticate the request.
    """

    city: str
    api_key: str


@dataclass
class WeatherResponse:
    """Represents a weather forecast response.

    Attributes:
        city: The city the forecast is for.
        temperature_c: Current temperature in Celsius.
        condition: Human-readable weather condition (e.g. "Sunny").
        humidity_pct: Relative humidity as a percentage (0–100).
    """

    city: str
    temperature_c: float
    condition: str
    humidity_pct: int
