"""Custom throttle classes for the shortener project."""

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Limit login attempts to 5 per minute per IP address.

    Uses the 'login' scope defined in DEFAULT_THROTTLE_RATES so the
    rate can be tuned via settings without touching code.
    """

    scope = "login"
