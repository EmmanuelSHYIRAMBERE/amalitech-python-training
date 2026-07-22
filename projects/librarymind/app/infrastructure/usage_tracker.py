"""In-memory AI usage and cost tracking."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Cost per 1 000 tokens (prompt / completion) in USD
PRICING: dict[str, dict[str, float]] = {
    "gpt-3.5-turbo": {"prompt": 0.0000005, "completion": 0.0000015},
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "claude-haiku-4-5": {"prompt": 0.00025, "completion": 0.00125},
    "claude-sonnet-4-6": {"prompt": 0.003, "completion": 0.015},
    "text-embedding-3-small": {"prompt": 0.00002, "completion": 0.0},
}


class UsageTracker:
    """Records AI token usage and calculates cost estimates.

    All records are held in memory; data is lost on restart.
    Each call to :meth:`record` appends one entry with a UTC timestamp,
    token counts, and a computed cost based on the :data:`PRICING` table.

    Example:
        >>> tracker = UsageTracker()
        >>> tracker.record("gpt-3.5-turbo", prompt_tokens=100,
        ...                completion_tokens=50, endpoint="/search/ask")
        >>> tracker.get_daily_cost()
        5e-05
    """

    def __init__(self) -> None:
        self.records: list[dict] = []

    def record(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        endpoint: str = "",
        cached: bool = False,
    ) -> None:
        """Append one usage record and log the cost.

        Args:
            model: Model identifier (must match a key in :data:`PRICING`
                to produce a non-zero cost estimate; unknown models use 0).
            prompt_tokens: Number of tokens in the prompt.
            completion_tokens: Number of tokens in the completion.
            endpoint: API path that triggered this call (for auditing).
            cached: ``True`` if the response was served from cache.
        """
        pricing = PRICING.get(model, {"prompt": 0.0, "completion": 0.0})
        cost_usd = (
            prompt_tokens / 1000 * pricing["prompt"]
            + completion_tokens / 1000 * pricing["completion"]
        )
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": cost_usd,
            "endpoint": endpoint,
            "cached": cached,
        }
        self.records.append(entry)
        logger.debug(f"Usage: {model} ${cost_usd:.6f} [{endpoint}]")

    def get_daily_cost(self) -> float:
        """Sum the cost of all records timestamped today (UTC).

        Returns:
            Total cost in USD for today's requests.
        """
        today = datetime.utcnow().date().isoformat()
        return sum(
            r["cost_usd"] for r in self.records if r["timestamp"].startswith(today)
        )

    def total_requests(self) -> int:
        """Return the total number of recorded requests since startup.

        Returns:
            Count of all entries in :attr:`records`.
        """
        return len(self.records)
