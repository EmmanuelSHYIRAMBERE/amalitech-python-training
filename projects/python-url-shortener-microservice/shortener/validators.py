"""Regex-based validators for the shortener app.

All patterns are compiled once at module level as re.Pattern[str] constants —
never inside functions, never uncompiled — following the same convention used
in the importer lab (validator.py) and the log analyzer lab (patterns.py).
"""

import re

# ---------------------------------------------------------------------------
# Short-code pattern
# Accepts 4–10 alphanumeric characters only.
# Rejects path-traversal attempts ("../admin"), XSS payloads ("<script>"),
# and URL-encoded spaces ("%20") that <str:short_code> would silently allow.
# ---------------------------------------------------------------------------
_SHORT_CODE_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9]{4,10}$")

# ---------------------------------------------------------------------------
# URL scheme pattern
# Enforces http:// or https:// prefix — Django's URLField accepts any scheme
# (ftp://, ftps://, etc.) by design, so this adds the stricter check.
# ---------------------------------------------------------------------------
_URL_SCHEME_PATTERN: re.Pattern[str] = re.compile(
    r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE
)


def validate_short_code(code: str) -> bool:
    """Return True if ``code`` matches the allowed short-code format.

    Args:
        code: The short code string to validate.

    Returns:
        ``True`` if the code is 4–10 alphanumeric characters, ``False`` otherwise.

    Example::

        >>> validate_short_code("aB3xYz")
        True
        >>> validate_short_code("../admin")
        False
    """
    return bool(_SHORT_CODE_PATTERN.fullmatch(code))


def validate_url_scheme(url: str) -> bool:
    """Return True if ``url`` starts with http:// or https://.

    Args:
        url: The URL string to validate.

    Returns:
        ``True`` if the URL has a valid http/https scheme, ``False`` otherwise.

    Example::

        >>> validate_url_scheme("https://example.com")
        True
        >>> validate_url_scheme("ftp://example.com")
        False
    """
    return bool(_URL_SCHEME_PATTERN.match(url))
