"""Resilient AI service with automatic provider fallback."""

import logging

from app.providers.base import AIProvider

logger = logging.getLogger(__name__)


class ResilientAIService:
    """Wraps a list of AI providers and falls back automatically on failure.

    Providers are tried in order.  If one raises any exception the next
    is tried.  If all providers fail, a ``RuntimeError`` is raised
    containing the last error.

    Args:
        providers: Ordered list of providers; index 0 is the primary.

    Example:
        >>> service = ResilientAIService([primary, fallback])
        >>> reply = service.generate("Hello")
    """

    def __init__(self, providers: list[AIProvider]) -> None:
        self.providers = providers

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generate a response, trying each provider in order.

        Args:
            prompt: The user-facing message content.
            system: System instruction prepended to the conversation.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in the completion response.

        Returns:
            The text content from the first provider that succeeds.

        Raises:
            RuntimeError: If every provider fails; the message includes
                the last underlying exception.
        """
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                logger.info(f"Trying provider: {provider.name}")
                result = provider.generate(prompt, system, temperature, max_tokens)
                logger.info(f"Provider {provider.name} succeeded")
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                last_error = e
        raise RuntimeError(f"All AI providers failed. Last error: {last_error}")

    def generate_with_history(
        self,
        messages: list[dict],
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generate a reply from a full messages array, with provider fallback.

        Args:
            messages: Ordered list of user/assistant turn dicts.
            system: System instruction (not included in messages).
            temperature: Sampling temperature.
            max_tokens: Maximum completion tokens.

        Returns:
            Text reply from the first provider that succeeds.

        Raises:
            RuntimeError: If every provider fails.
        """
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                logger.info(f"Trying provider (history): {provider.name}")
                result = provider.generate_with_history(
                    messages, system, temperature, max_tokens
                )
                logger.info(f"Provider {provider.name} succeeded")
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                last_error = e
        raise RuntimeError(f"All AI providers failed. Last error: {last_error}")

    @property
    def primary_provider_name(self) -> str:
        """Name of the first (primary) provider.

        Returns:
            Provider name string, or ``"none"`` if the list is empty.
        """
        return self.providers[0].name if self.providers else "none"
