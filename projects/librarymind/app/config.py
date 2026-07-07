"""Application configuration loaded from environment variables / .env."""

import logging

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic-settings model for all LibraryMind configuration.

    Every value is read exclusively from environment variables or the
    ``.env`` file — there are no hardcoded defaults in this class.
    A missing or placeholder ``AMALI_API_KEY`` causes an immediate
    ``ValidationError`` so the application fails loudly on misconfiguration.

    Example:
        >>> from app.config import settings
        >>> print(settings.PRIMARY_PROVIDER)
        openai
    """

    # Amalitec proxy — replaces direct provider keys
    AMALI_API_KEY: str = Field(..., description="Amalitec proxy API key (required)")
    AMALI_BASE_URL: str = Field(..., description="Amalitec proxy base URL")

    # Which provider the proxy should route to
    PRIMARY_PROVIDER: str = Field(
        ..., description="Primary AI provider: openai or anthropic"
    )
    FALLBACK_PROVIDER: str = Field(
        ..., description="Fallback AI provider if primary fails"
    )

    # Models
    OPENAI_MODEL: str = Field(
        ..., description="Model name forwarded for OpenAI routing"
    )
    ANTHROPIC_MODEL: str = Field(
        ..., description="Model name forwarded for Anthropic routing"
    )

    # Infrastructure
    REDIS_URL: str = Field(..., description="Redis connection URL")
    RATE_LIMIT_PER_MINUTE: int = Field(
        ..., description="Max AI requests per minute (token bucket capacity)"
    )
    CACHE_TTL_SECONDS: int = Field(..., description="Redis cache TTL in seconds")
    RELEVANCE_THRESHOLD: float = Field(
        ..., description="Minimum cosine similarity to include a book result"
    )
    MAX_HISTORY_MESSAGES: int = Field(
        ..., description="Max chat turns retained per session"
    )
    EMBEDDING_MODEL: str = Field(
        ..., description="Embedding model name (interface compatibility)"
    )
    CHROMA_DB_PATH: str = Field(
        ..., description="Filesystem path for ChromaDB persistence"
    )

    # Public (unauthenticated) access limits
    PUBLIC_SEARCH_LIMIT: int = Field(
        ...,
        description="Max results returned to unauthenticated callers on /search/books",
    )

    # Authentication
    JWT_SECRET_KEY: str = Field(..., description="Secret key for signing JWT tokens")
    JWT_ALGORITHM: str = Field(..., description="JWT signing algorithm (e.g. HS256)")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        ..., description="JWT token lifetime in minutes"
    )

    @model_validator(mode="after")
    def api_key_must_be_set(self) -> "Settings":
        """Validate that AMALI_API_KEY is present and non-placeholder.

        Raises:
            ValueError: When the key is empty or still set to the
                example placeholder value.
        """
        if not self.AMALI_API_KEY or self.AMALI_API_KEY == "your_amali_key_here":
            raise ValueError(
                "Set AMALI_API_KEY in your .env file. "
                "Get your key from https://ai-api.amalitech.org"
            )
        return self

    class Config:
        env_file = ".env"


settings = Settings()


def validate_and_summarise() -> None:
    """Print a startup configuration summary to aid debugging.

    Logs the active configuration (with secrets masked) so
    operators can verify the application is correctly configured
    without exposing sensitive values.
    """
    logger = logging.getLogger(__name__)
    masked_key = (
        settings.AMALI_API_KEY[:8] + "..." if len(settings.AMALI_API_KEY) > 8 else "***"
    )
    logger.info("Configuration loaded:")
    logger.info(f"  AMALI_API_KEY          : {masked_key}")
    logger.info(f"  AMALI_BASE_URL         : {settings.AMALI_BASE_URL}")
    logger.info(f"  PRIMARY_PROVIDER       : {settings.PRIMARY_PROVIDER}")
    logger.info(f"  FALLBACK_PROVIDER      : {settings.FALLBACK_PROVIDER}")
    logger.info(f"  OPENAI_MODEL           : {settings.OPENAI_MODEL}")
    logger.info(f"  ANTHROPIC_MODEL        : {settings.ANTHROPIC_MODEL}")
    logger.info(f"  REDIS_URL              : {settings.REDIS_URL}")
    logger.info(f"  RATE_LIMIT_PER_MINUTE  : {settings.RATE_LIMIT_PER_MINUTE}")
    logger.info(f"  CACHE_TTL_SECONDS      : {settings.CACHE_TTL_SECONDS}")
    logger.info(f"  RELEVANCE_THRESHOLD    : {settings.RELEVANCE_THRESHOLD}")
    logger.info(f"  MAX_HISTORY_MESSAGES   : {settings.MAX_HISTORY_MESSAGES}")
    logger.info(f"  EMBEDDING_MODEL        : {settings.EMBEDDING_MODEL}")
    logger.info(f"  CHROMA_DB_PATH         : {settings.CHROMA_DB_PATH}")
    logger.info(f"  PUBLIC_SEARCH_LIMIT    : {settings.PUBLIC_SEARCH_LIMIT}")
    logger.info(f"  JWT_ALGORITHM          : {settings.JWT_ALGORITHM}")
    logger.info(
        f"  JWT_EXPIRE_MINUTES     : {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}"
    )
