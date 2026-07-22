"""Support ticket classification service."""

import json
import logging
import re

from app.exceptions import ClassificationError

logger = logging.getLogger(__name__)


class ClassificationService:
    """Classifies library support tickets into structured JSON.

    Uses the AI service at low temperature (0.1) for consistent,
    deterministic output.  Markdown code fences are stripped before
    JSON parsing.

    Args:
        ai_service: Resilient AI service for text generation.
        rate_limiter: Token-bucket limiter; raises on exhaustion.

    Example:
        >>> svc = ClassificationService(ai_service, rate_limiter)
        >>> result = svc.classify("My card is broken and I'm frustrated")
        >>> print(result["category"])   # "technical"
        >>> print(result["sentiment"])  # "negative"
    """

    def __init__(self, ai_service, rate_limiter) -> None:
        self.ai_service = ai_service
        self.rate_limiter = rate_limiter

    def classify(self, ticket_text: str) -> dict:
        """Classify a support ticket into a structured JSON object.

        Args:
            ticket_text: Raw text of the support ticket.

        Returns:
            Dict with keys: ``category``, ``priority``, ``sentiment``,
            ``department``, ``summary``.

        Raises:
            RateLimitError: When the rate-limit bucket is empty.
            ClassificationError: When the AI returns non-parseable JSON.
        """
        self.rate_limiter.acquire()

        system = (
            "You are a library support ticket classifier.\n"
            "Respond ONLY with a valid JSON object. "
            "No markdown code fences. No explanation. "
            "No text before or after the JSON.\n"
            "Use exactly this schema:\n"
            "{\n"
            '  "category": one of '
            '"account","borrowing","technical","complaint",'
            '"suggestion","general",\n'
            '  "priority": one of "low","medium","high","urgent",\n'
            '  "sentiment": one of "positive","neutral","negative",\n'
            '  "department": "one short routing phrase",\n'
            '  "summary": "one sentence describing the issue"\n'
            "}"
        )

        raw = self.ai_service.generate(
            prompt=f"Classify this support ticket:\n\n{ticket_text}",
            system=system,
            temperature=0.1,
            max_tokens=200,
        )
        return self._parse_json(raw)

    def _parse_json(self, raw: str) -> dict:
        """Strip markdown fences and parse the AI response as JSON.

        Args:
            raw: Raw string response from the AI (may contain fences).

        Returns:
            Parsed dict from the cleaned JSON.

        Raises:
            ClassificationError: When ``json.loads`` fails after
                stripping fences.
        """
        clean = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed. Raw: {raw!r}")
            raise ClassificationError(
                f"AI returned invalid JSON: {e}. Raw: {raw[:200]}"
            ) from e
