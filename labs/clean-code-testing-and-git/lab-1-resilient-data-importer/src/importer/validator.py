"""Validation component for the Resilient Data Importer.

Responsible solely for asserting that a ``User`` object's fields satisfy
the business rules before it is persisted.  Raises ``ValidationError`` on
the first failing rule so the caller can decide whether to skip or abort.
"""

import logging
import re

from importer.exceptions import ValidationError
from importer.models import User

logger = logging.getLogger(__name__)

# RFC-5321-inspired pattern — intentionally pragmatic, not exhaustive.
_EMAIL_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


def validate_user(user: User) -> None:
    """Validate all fields of a ``User`` record.

    Checks are applied in order: user_id → name → email.  The first
    failing check raises immediately so the error message is precise.

    Args:
        user: The ``User`` instance to validate.

    Raises:
        ValidationError: If ``user_id`` is empty, ``name`` is blank, or
            ``email`` does not match the expected format.

    Example:
        >>> from importer.models import User
        >>> validate_user(User("U1", "Alice", "alice@example.com"))  # OK
        >>> validate_user(User("", "Alice", "alice@example.com"))
        ValidationError: user_id is empty ...
    """
    if not user.user_id.strip():
        raise ValidationError(f"user_id is empty for record: {user!r}")

    if not user.name.strip():
        raise ValidationError(f"name is empty for user_id: '{user.user_id}'")

    if not _EMAIL_PATTERN.match(user.email):
        raise ValidationError(
            f"Invalid email '{user.email}' for user_id: '{user.user_id}'"
        )

    logger.debug("Validation passed for user_id: '%s'", user.user_id)
