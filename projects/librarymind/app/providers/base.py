"""Abstract base class for AI provider implementations."""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Contract that every AI backend must satisfy.

    Concrete implementations (e.g. AmaliProvider) plug into
    ResilientAIService by fulfilling this interface.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generate a text completion for the given prompt.

        Args:
            prompt: The user-facing message content.
            system: System instruction prepended to the conversation.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in the completion response.

        Returns:
            The text content of the AI response.

        Raises:
            RuntimeError: If the provider fails to return a response.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier for this provider (e.g. ``"openai"``).

        Returns:
            Provider name string used in logging and routing headers.
        """
