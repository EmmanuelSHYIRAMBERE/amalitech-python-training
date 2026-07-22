"""Custom exceptions for the LibraryMind application.

All application-specific exceptions inherit from LibraryMindError,
making it easy to catch any application error with a single
except clause.
"""


class LibraryMindError(Exception):
    """Base exception for all LibraryMind errors."""

    pass


class AIProviderError(LibraryMindError):
    """Raised when all AI providers fail after retries.

    Args:
        message: Description of the failure.
        last_error: The underlying exception from the last provider.
    """

    def __init__(self, message: str, last_error: Exception = None) -> None:
        super().__init__(message)
        self.last_error = last_error


class RateLimitError(LibraryMindError):
    """Raised when the application rate limit is exceeded."""

    pass


class EmbeddingError(LibraryMindError):
    """Raised when embedding generation fails."""

    pass


class VectorStoreError(LibraryMindError):
    """Raised when ChromaDB operations fail."""

    pass


class ClassificationError(LibraryMindError):
    """Raised when the AI returns invalid JSON for classification."""

    pass


class SummarisationError(LibraryMindError):
    """Raised when the AI returns invalid JSON for summarisation."""

    pass
