"""JSON-backed storage repository for the Resilient Data Importer.

Implements the Repository pattern: the rest of the application talks to
``UserRepository`` and never touches the JSON file directly.  A private
context manager (``_open_db``) guarantees that the file is always written
back — even if an exception occurs mid-operation — preventing data loss.
"""

import json
import logging
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from importer.exceptions import DuplicateUserError
from importer.models import User

logger = logging.getLogger(__name__)

# Type alias for the in-memory database structure.
_DbDict = dict[str, dict[str, str]]


@contextmanager
def _open_db(db_path: Path) -> Generator[_DbDict, None, None]:
    """Context manager for safe, atomic read/write of the JSON database.

    Loads the existing database on entry.  On exit (normal *or* exceptional)
    the potentially-modified dict is written back to disk, so partial updates
    are never silently discarded.

    Args:
        db_path: Path to the JSON file used as the database.

    Yields:
        The current database contents as a ``dict`` keyed by ``user_id``.

    Example:
        >>> with _open_db(Path("db.json")) as db:
        ...     db["U001"] = {"name": "Alice", ...}
        # db.json is written here automatically
    """
    data: _DbDict = {}

    # Load existing data if the file already exists.
    if db_path.exists():
        with db_path.open(encoding="utf-8") as fh:
            data = json.load(fh)

    try:
        yield data
    finally:
        # Always write back — this is the "safe write" guarantee.
        with db_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        logger.debug("Database persisted to '%s'", db_path)


class UserRepository:
    """Handles persistence of ``User`` records to a JSON file.

    Each ``save`` call opens the database, checks for duplicates, inserts
    the new record, and closes (writes) the database — all within the
    ``_open_db`` context manager.

    Args:
        db_path: Path to the JSON file that acts as the database.

    Example:
        >>> repo = UserRepository(Path("database.json"))
        >>> repo.save(User("U001", "Alice", "alice@example.com"))
        >>> repo.count()
        1
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def save(self, user: User) -> None:
        """Persist a single ``User`` to the JSON database.

        Args:
            user: The ``User`` instance to store.

        Raises:
            DuplicateUserError: If a record with the same ``user_id``
                already exists in the database.
        """
        with _open_db(self._db_path) as db:
            if user.user_id in db:
                raise DuplicateUserError(user.user_id)
            db[user.user_id] = user.to_dict()
            logger.info("Saved user '%s' (%s)", user.name, user.user_id)

    def count(self) -> int:
        """Return the total number of users currently in the database.

        Returns:
            Integer count of stored user records, or ``0`` if the database
            file does not yet exist.
        """
        if not self._db_path.exists():
            return 0
        with self._db_path.open(encoding="utf-8") as fh:
            return len(json.load(fh))

    def exists(self, user_id: str) -> bool:
        """Check whether a user_id is already present in the database.

        Args:
            user_id: The user ID to look up.

        Returns:
            ``True`` if the user exists, ``False`` otherwise.
        """
        if not self._db_path.exists():
            return False
        with self._db_path.open(encoding="utf-8") as fh:
            return user_id in json.load(fh)
