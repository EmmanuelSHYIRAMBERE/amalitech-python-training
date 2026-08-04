"""CSV parsing component for the Resilient Data Importer.

Responsible solely for reading a CSV file and yielding ``User`` objects.
All I/O and format errors are surfaced as ``FileFormatError`` so the caller
does not need to handle raw ``OSError`` or ``csv`` exceptions.
"""

import csv
import logging
from collections.abc import Iterator
from pathlib import Path

from importer.exceptions import FileFormatError
from importer.models import User

logger = logging.getLogger(__name__)

# The set of column names that every valid CSV file must contain.
REQUIRED_COLUMNS: frozenset[str] = frozenset({"user_id", "name", "email"})


def parse_csv(file_path: Path) -> Iterator[User]:
    """Parse a CSV file and yield one ``User`` per data row.

    Opens the file, validates that the required columns are present, then
    iterates row-by-row.  Rows that are missing expected keys or contain
    ``None`` values are skipped with a warning rather than aborting the
    entire import.

    Args:
        file_path: Absolute or relative ``Path`` to the CSV file.

    Yields:
        A ``User`` instance for each well-formed data row.

    Raises:
        FileFormatError: If the file does not exist, cannot be read, or
            lacks one or more of the required columns.

    Example:
        >>> from pathlib import Path
        >>> for user in parse_csv(Path("users.csv")):
        ...     print(user.name)
    """
    if not file_path.exists():
        raise FileFormatError(f"File not found: {file_path}")

    try:
        with file_path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)

            # Validate header row before touching any data rows.
            if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(
                set(reader.fieldnames)
            ):
                raise FileFormatError(
                    f"CSV must contain columns {sorted(REQUIRED_COLUMNS)}. "
                    f"Got: {reader.fieldnames}"
                )

            for line_num, row in enumerate(reader, start=2):
                try:
                    yield User(
                        user_id=row["user_id"].strip(),
                        name=row["name"].strip(),
                        email=row["email"].strip(),
                    )
                except (KeyError, AttributeError) as exc:
                    # Individual malformed rows are skipped, not fatal.
                    logger.warning(
                        "Skipping malformed row at line %d: %s", line_num, exc
                    )

    except OSError as exc:
        raise FileFormatError(f"Cannot read file '{file_path}': {exc}") from exc
