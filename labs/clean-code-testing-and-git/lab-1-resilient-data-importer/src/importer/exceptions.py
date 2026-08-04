"""Custom exception hierarchy for the Resilient Data Importer.

All application-specific exceptions inherit from ImporterError so callers
can catch the entire family with a single except clause when needed.
"""


class ImporterError(Exception):
    """Base exception for all importer errors.

    All other custom exceptions in this package inherit from this class,
    allowing callers to catch any importer-related error with a single
    ``except ImporterError`` clause.
    """


class FileFormatError(ImporterError):
    """Raised when the CSV file is missing, unreadable, or malformed.

    Examples:
        - File does not exist at the given path.
        - File is missing one or more required columns.
        - File cannot be opened due to OS-level permission errors.
    """


class DuplicateUserError(ImporterError):
    """Raised when a user with the same user_id already exists in the database.

    Args:
        user_id: The duplicate user ID that triggered the error.

    Example:
        >>> raise DuplicateUserError("U001")
    """

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User '{user_id}' already exists in the database.")


class ValidationError(ImporterError):
    """Raised when a user record fails field-level data validation.

    Examples:
        - user_id is an empty string.
        - name is blank or too short.
        - email does not match the expected format.
    """
