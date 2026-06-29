"""Book review summarisation service."""

import json
import logging
import re

from app.exceptions import SummarisationError

logger = logging.getLogger(__name__)


class SummarisationService:
    """Summarises a batch of book reviews into structured JSON.

    Analyses all reviews holistically to identify patterns, not
    per-review breakdowns.  Uses temperature 0.2 for near-deterministic
    output while allowing slight variation in phrasing.

    Args:
        ai_service: Resilient AI service for text generation.
        rate_limiter: Token-bucket limiter; raises on exhaustion.

    Example:
        >>> svc = SummarisationService(ai_service, rate_limiter)
        >>> result = svc.summarise(["Great book!", "Slow pacing."])
        >>> print(result["overall_sentiment"])  # "mixed"
        >>> print(result["average_rating"])     # e.g. 3.5
    """

    def __init__(self, ai_service, rate_limiter) -> None:
        self.ai_service   = ai_service
        self.rate_limiter = rate_limiter

    def summarise(self, reviews: list[str]) -> dict:
        """Summarise 1–50 book reviews into a structured analysis.

        Args:
            reviews: List of 1–50 review strings to analyse.

        Returns:
            Dict with keys: ``overall_sentiment``, ``average_rating``
            (float 1.0–5.0), ``key_themes`` (list), ``praise`` (list),
            ``criticism`` (list), ``recommendation`` (str).

        Raises:
            ValueError: When ``reviews`` is empty or exceeds 50 items.
            RateLimitError: When the rate-limit bucket is empty.
            SummarisationError: When the AI returns non-parseable JSON.
        """
        if not reviews:
            raise ValueError("At least one review is required")
        if len(reviews) > 50:
            raise ValueError("Maximum 50 reviews allowed")

        self.rate_limiter.acquire()

        numbered = "\n".join(
            f"{i+1}. {r}" for i, r in enumerate(reviews)
        )

        system = (
            "You are a literary analyst.\n"
            "Analyse ALL reviews holistically — identify overall "
            "patterns across the set, not each review individually.\n"
            "Respond ONLY with a valid JSON object. "
            "No markdown fences. No explanation. "
            "No text before or after the JSON.\n"
            "Use exactly this schema:\n"
            "{\n"
            '  "overall_sentiment": one of '
            '"positive","mixed","negative",\n'
            '  "average_rating": a float between 1.0 and 5.0,\n'
            '  "key_themes": ["theme1", "theme2"],\n'
            '  "praise": ["common point of praise"],\n'
            '  "criticism": ["common point of criticism"],\n'
            '  "recommendation": "one sentence recommendation"\n'
            "}"
        )

        raw = self.ai_service.generate(
            prompt=f"Analyse these book reviews:\n\n{numbered}",
            system=system,
            temperature=0.2,
            max_tokens=400,
        )
        return self._parse_json(raw)

    def _parse_json(self, raw: str) -> dict:
        """Strip markdown fences and parse the AI response as JSON.

        Args:
            raw: Raw string response from the AI (may contain fences).

        Returns:
            Parsed dict from the cleaned JSON.

        Raises:
            SummarisationError: When ``json.loads`` fails after
                stripping fences.
        """
        clean = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed. Raw: {raw!r}")
            raise SummarisationError(
                f"AI returned invalid JSON: {e}. Raw: {raw[:200]}"
            ) from e
