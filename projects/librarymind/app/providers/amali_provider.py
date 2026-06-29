"""Amalitec proxy AI provider implementation."""

import logging

import httpx
from tenacity import (
    before_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from app.providers.base import AIProvider

logger = logging.getLogger(__name__)


class AmaliProvider(AIProvider):
    """AI provider that routes requests through the Amalitec proxy.

    Supports both ``openai`` and ``anthropic`` as backends by setting
    the ``Provider`` request header accordingly.  Retries up to 3 times
    with exponential backoff on transient failures.

    Response format differs by provider:
      - openai:    OpenAI chat completions → ``choices[0].message.content``
      - anthropic: Anthropic messages API  → ``content[0].text``

    Args:
        api_key: Amalitec API key sent as ``X-Api-Key`` header.
        base_url: Full base URL of the proxy (trailing slash optional).
        provider_name: Backend to route to — ``"openai"`` or ``"anthropic"``.
        model: Model identifier forwarded to the backend.

    Example:
        >>> provider = AmaliProvider(
        ...     api_key="key", base_url="https://ai-api.amalitech.org/api/v2/public/",
        ...     provider_name="openai", model="gpt-3.5-turbo"
        ... )
        >>> reply = provider.generate("Say hello", temperature=0.0)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        provider_name: str,
        model: str,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") + "/"
        self._provider_name = provider_name
        self.model = model
        # verify=False: Amalitec proxy cert chain is not in the local Windows
        # trust store on some machines. Safe for this known training proxy.
        self.client = httpx.Client(timeout=30.0, verify=False)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before=before_log(logger, logging.WARNING),
        reraise=True,
    )
    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Send a prompt to the Amalitec proxy and return the text response.

        Calls the proxy with the configured ``Provider`` header (openai or
        anthropic).  Retries up to 3 times with exponential backoff before
        raising.  Handles both OpenAI and Anthropic native response formats.

        Args:
            prompt: The user-facing message content.
            system: The system instruction prompt.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in the completion response.

        Returns:
            The text content of the AI response.

        Raises:
            RuntimeError: If the proxy returns a non-200 status after
                all retries are exhausted, or if the response shape is
                unrecognised.

        Example:
            >>> provider = AmaliProvider(api_key="key", base_url="...",
            ...     provider_name="openai", model="gpt-3.5-turbo")
            >>> reply = provider.generate("Say hello", temperature=0.0)
            >>> print(reply)
            Hello!
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "accept":        "application/json",
            "Content-Type":  "application/json",
            "X-Api-Key":     self.api_key,
            "Provider":      self._provider_name,
        }

        response = self.client.post(
            self.base_url,
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Amalitec proxy error {response.status_code} "
                f"(provider={self._provider_name}): {response.text[:300]}"
            )

        data = response.json()
        return self._extract_text(data)

    def _extract_text(self, data: dict) -> str:
        """Normalise the proxy response to a plain text string.

        Handle both response shapes the proxy may return:
          - OpenAI format:    ``data["choices"][0]["message"]["content"]``
          - Anthropic format: ``data["content"][0]["text"]``

        Args:
            data: Parsed JSON response body from the proxy.

        Returns:
            The text content extracted from the response.

        Raises:
            RuntimeError: If the response does not match either known shape.
        """
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        if "content" in data:
            return data["content"][0]["text"]
        raise RuntimeError(
            f"Unrecognised response shape from proxy "
            f"(provider={self._provider_name}): {str(data)[:200]}"
        )

    @property
    def name(self) -> str:
        """Provider name used in the ``Provider`` routing header.

        Returns:
            One of ``"openai"`` or ``"anthropic"``.
        """
        return self._provider_name
