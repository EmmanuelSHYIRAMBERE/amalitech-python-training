"""Data models for the Resilient Data Importer.

Defines the User dataclass used as the canonical in-memory representation
of a single record parsed from the CSV source file.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class User:
    """Represents a single user record parsed from a CSV file.

    Attributes:
        user_id: Unique identifier for the user (e.g. ``"U001"``).
        name: Full display name of the user.
        email: Email address of the user.
        imported_at: ISO-8601 UTC timestamp set automatically at creation.

    Example:
        >>> user = User(user_id="U001", name="Alice", email="alice@example.com")
        >>> user.user_id
        'U001'
    """

    user_id: str
    name: str
    email: str
    imported_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, str]:
        """Serialize the User instance to a plain dictionary.

        Returns:
            A dict with keys ``user_id``, ``name``, ``email``,
            and ``imported_at``.
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "imported_at": self.imported_at,
        }
