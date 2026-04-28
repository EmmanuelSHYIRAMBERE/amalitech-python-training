"""Application-level exceptions for the shortener app.

Mirrors the exception hierarchy pattern from Clean Code Lab 1
(ImporterError → FileFormatError, DuplicateUserError, ValidationError).

Hierarchy::

    ShortenerError          ← base; catch-all for this app
    ├── ShortLinkError      ← link lifecycle problems
    │   ├── ShortLinkInactiveError   ← link is deactivated (is_active=False)
    │   └── ShortLinkExpiredError    ← link has passed its expires_at
    └── ShortCodeError      ← code generation problems
        └── ShortCodeCollisionError  ← generator exhausted retries
"""


class ShortenerError(Exception):
    """Base exception for all shortener application errors."""


# ---------------------------------------------------------------------------
# Link lifecycle
# ---------------------------------------------------------------------------


class ShortLinkError(ShortenerError):
    """Raised for problems related to a short link's lifecycle state."""


class ShortLinkInactiveError(ShortLinkError):
    """Raised when a redirect is attempted on a deactivated link.

    Args:
        short_code: The short code that was looked up.

    Example::

        raise ShortLinkInactiveError("aB3xYz")
    """

    def __init__(self, short_code: str) -> None:
        self.short_code = short_code
        super().__init__(f"Short link '{short_code}' is inactive.")


class ShortLinkExpiredError(ShortLinkError):
    """Raised when a redirect is attempted on an expired link.

    Args:
        short_code: The short code that was looked up.

    Example::

        raise ShortLinkExpiredError("aB3xYz")
    """

    def __init__(self, short_code: str) -> None:
        self.short_code = short_code
        super().__init__(f"Short link '{short_code}' has expired.")


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------


class ShortCodeError(ShortenerError):
    """Raised for problems during short code generation."""


class ShortCodeCollisionError(ShortCodeError):
    """Raised when the generator cannot produce a unique short code.

    This happens when all retry attempts result in a code that already
    exists in the database — extremely unlikely in practice but must be
    handled gracefully.

    Args:
        attempts: Number of generation attempts made before giving up.

    Example::

        raise ShortCodeCollisionError(attempts=5)
    """

    def __init__(self, attempts: int) -> None:
        self.attempts = attempts
        super().__init__(
            f"Could not generate a unique short code after {attempts} attempts."
        )
