"""Application configuration loaded from environment variables / .env."""

import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic-settings model for all LibraryMind configuration.

    Values are read from environment variables or a ``.env`` file in the
    working directory.  ``AMALI_API_KEY`` is required and validated on
    startup; the application will not start without a real key.

    Example:
        >>> from app.config import settings
        >>> print(settings.PRIMARY_PROVIDER)
        openai
    """

    # Amalitec proxy — replaces direct provider keys
    AMALI_API_KEY: str = ""
    AMALI_BASE_URL: str = "https://ai-api.amalitech.org/api/v2/public/"

    # Which provider the proxy should route to
    PRIMARY_PROVIDER: str = "openai"  # "openai" or "anthropic"
    FALLBACK_PROVIDER: str = "anthropic"  # used if primary fails

    # Models
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    ANTHROPIC_MODEL: str = "claude-haiku-4-5"

    # Infrastructure
    REDIS_URL: str = "redis://localhost:6379"
    RATE_LIMIT_PER_MINUTE: int = 20
    CACHE_TTL_SECONDS: int = 3600
    RELEVANCE_THRESHOLD: float = 0.05
    MAX_HISTORY_MESSAGES: int = 10
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHROMA_DB_PATH: str = "./chroma_db"

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
    logger.info(f"  AMALI_API_KEY     : {masked_key}")
    logger.info(f"  PRIMARY_PROVIDER  : {settings.PRIMARY_PROVIDER}")
    logger.info(f"  FALLBACK_PROVIDER : {settings.FALLBACK_PROVIDER}")
    logger.info(f"  OPENAI_MODEL      : {settings.OPENAI_MODEL}")
    logger.info(f"  ANTHROPIC_MODEL   : {settings.ANTHROPIC_MODEL}")
    logger.info(f"  REDIS_URL         : {settings.REDIS_URL}")
    logger.info(f"  THRESHOLD         : {settings.RELEVANCE_THRESHOLD}")
    logger.info(f"  CHROMA_DB_PATH    : {settings.CHROMA_DB_PATH}")
