"""Value objects and data structures for the preview domain.

Demonstrates:
- frozen dataclass (immutable value object)
- NamedTuple for lightweight structured data
- @property decorators
- collections: Counter, defaultdict, OrderedDict, deque
- Numerical operations and loops in analytics
- Type hints: Optional, Union, Dict, List
"""
from __future__ import annotations

import logging
from collections import Counter, OrderedDict, defaultdict, deque
from collections import Counter as CounterType
from dataclasses import dataclass, field
from typing import NamedTuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# NamedTuple — lightweight, memory-efficient, immutable
# ---------------------------------------------------------------------------


class DomainInfo(NamedTuple):
    """Parsed URL components."""

    scheme: str
    netloc: str
    path: str

    @property
    def base_url(self) -> str:
        return f"{self.scheme}://{self.netloc}"


# ---------------------------------------------------------------------------
# Frozen dataclass — the primary value object, matches url_preview contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PreviewResult:
    """Immutable result of a URL preview fetch.

    CONTRACT: This dataclass must match the shape expected by
    shortener/preview_client.py in the url-shortener service.
    All fields nullable — a partial result is still useful.
    """

    url: str
    title: str | None = field(default=None)
    description: str | None = field(default=None)
    favicon: str | None = field(default=None)
    error: str | None = field(default=None)

    @property
    def is_success(self) -> bool:
        """True if at least one metadata field was populated."""
        return any([self.title, self.description, self.favicon])

    @property
    def metadata_fields(self) -> dict[str, str | None]:
        """Return a dict of only the metadata fields (no url/error)."""
        return {
            "title": self.title,
            "description": self.description,
            "favicon": self.favicon,
        }


# ---------------------------------------------------------------------------
# Collections-based analytics — demonstrates Counter, defaultdict, deque
# ---------------------------------------------------------------------------


class FetchStats:
    """Tracks fetch outcomes using built-in collections.

    Demonstrates:
    - Counter for outcome frequency
    - defaultdict for domain grouping
    - OrderedDict for sorted summaries
    - deque for bounded recent-event window
    - Numerical operations: percentage, totals, averages
    """

    def __init__(self, window: int = 1000) -> None:
        # Counter: count outcomes (success, circuit_open, http_error, etc.)
        self.outcome_counter: CounterType[str] = Counter()
        # defaultdict: group failed URLs by domain
        self.failures_by_domain: dict[str, list[str]] = defaultdict(list)
        # OrderedDict: top domains by fetch count (populated on demand)
        self.top_domains: OrderedDict[str, int] = OrderedDict()
        # deque: bounded window of recent results
        self.recent: deque[PreviewResult] = deque(maxlen=window)
        self._domain_counter: CounterType[str] = Counter()

    def record(self, result: PreviewResult, domain: str) -> None:
        """Record one fetch outcome."""
        outcome = "success" if result.is_success else (
            "circuit_open" if result.error and "circuit" in result.error.lower()
            else "failure"
        )
        self.outcome_counter[outcome] += 1
        self._domain_counter[domain] += 1
        self.recent.append(result)

        if not result.is_success and result.error:
            self.failures_by_domain[domain].append(result.error)

    def summary(self) -> dict:
        """Compute summary statistics — loops + numerical ops."""
        total = sum(self.outcome_counter.values())
        top = self._domain_counter.most_common(10)
        self.top_domains = OrderedDict(top)

        breakdown = [
            {
                "outcome": outcome,
                "count": count,
                "percentage": round(count / total * 100, 2) if total > 0 else 0.0,
            }
            for outcome, count in self.outcome_counter.most_common()
        ]
        return {
            "total_fetches": total,
            "outcomes": breakdown,
            "top_domains": list(top),
        }
