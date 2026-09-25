"""AI Gateway provider implementation (OpenAI-compatible /v1 API)."""

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
    """AI provider that routes requests through the AI Gateway.

    The gateway exposes a standard OpenAI-compatible ``/v1/chat/completions``
    endpoint; the backend model (OpenAI, Anthropic, etc.) is selected purely
    by the ``model`` name in the request payload, not by a routing header.
    ``provider_name`` is kept only as a local label (used for logging and
    for ``ResilientAIService``'s fallback ordering) — it is never sent to
    the gateway itself. Retries up to 3 times with exponential backoff on
    transient failures.

    Args:
        api_key: Gateway API key sent as a ``Bearer`` token.
        base_url: Gateway base URL, e.g. ``https://ai-gateway.amalitech.org/v1``.
        provider_name: Local label for this provider — ``"openai"`` or
            ``"anthropic"`` — used for logging/fallback ordering only.
        model: Model identifier forwarded to the gateway (e.g.
            ``"gpt-4o-mini"``, ``"claude-sonnet-4-6"``).

    Example:
        >>> provider = AmaliProvider(
        ...     api_key="key", base_url="https://ai-gateway.amalitech.org/v1",
        ...     provider_name="openai", model="gpt-4o-mini"
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
        self.base_url = base_url.rstrip("/") + "/chat/completions"
        self._provider_name = provider_name
        self.model = model
        # verify=False: gateway cert chain is not in the local Windows
        # trust store on some machines. Safe for this known training gateway.
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
        """Send a prompt to the AI Gateway and return the text response.

        Calls the gateway's ``/chat/completions`` endpoint with the
        configured ``model``.  Retries up to 3 times with exponential
        backoff before raising.  Handles both OpenAI and Anthropic native
        response formats (the gateway itself always returns OpenAI-shaped
        responses, but the fallback detection is kept for resilience).

        Args:
            prompt: The user-facing message content.
            system: The system instruction prompt.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in the completion response.

        Returns:
            The text content of the AI response.

        Raises:
            RuntimeError: If the gateway returns a non-200 status after
                all retries are exhausted, or if the response shape is
                unrecognised.

        Example:
            >>> provider = AmaliProvider(api_key="key", base_url="...",
            ...     provider_name="openai", model="gpt-4o-mini")
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
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = self.client.post(
            self.base_url,
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"AI Gateway error {response.status_code} "
                f"(provider={self._provider_name}, model={self.model}): {response.text[:300]}"
            )

        data = response.json()
        return self._extract_text(data)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before=before_log(logger, logging.WARNING),
        reraise=True,
    )
    def generate_with_history(
        self,
        messages: list[dict],
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Send a full conversation messages array to the AI Gateway.

        Builds the payload with the system message first, then appends
        the provided history messages directly so the AI sees the real
        conversation structure rather than a flattened string.

        Args:
            messages: Ordered list of ``{"role": ..., "content": ...}``
                dicts (user and assistant turns only — no system).
            system: System instruction sent as the first message.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in the completion response.

        Returns:
            The text content of the AI response.

        Raises:
            RuntimeError: On non-200 gateway response after all retries.
        """
        payload_messages = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        payload_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": payload_messages,
            "stream": False,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        response = self.client.post(self.base_url, json=payload, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(
                f"AI Gateway error {response.status_code} "
                f"(provider={self._provider_name}, model={self.model}): {response.text[:300]}"
            )
        return self._extract_text(response.json())

    def _extract_text(self, data: dict) -> str:
        """Normalise the gateway response to a plain text string.

        Handle both response shapes that may be encountered:
          - OpenAI format:    ``data["choices"][0]["message"]["content"]``
          - Anthropic format: ``data["content"][0]["text"]``

        The gateway always returns OpenAI-shaped responses regardless of
        the underlying model; the Anthropic-shape check is kept in case
        that ever changes.

        Args:
            data: Parsed JSON response body from the gateway.

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
            f"Unrecognised response shape from gateway "
            f"(provider={self._provider_name}): {str(data)[:200]}"
        )

    @property
    def name(self) -> str:
        """Provider name used in the ``Provider`` routing header.

        Returns:
            One of ``"openai"`` or ``"anthropic"``.
        """
        return self._provider_name
