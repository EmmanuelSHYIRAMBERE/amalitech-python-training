"""Tests for preview.schemas — value objects, NamedTuple, collections.

Demonstrates:
- Testing frozen dataclasses (immutability)
- Testing @property decorators
- Testing Counter, defaultdict, deque, OrderedDict via FetchStats
- Numerical operations in statistics
"""
from __future__ import annotations

import pytest

from preview.schemas import DomainInfo, FetchStats, PreviewResult


# ---------------------------------------------------------------------------
# DomainInfo NamedTuple
# ---------------------------------------------------------------------------


class TestDomainInfo:
    def test_base_url_property(self):
        info = DomainInfo(scheme="https", netloc="example.com", path="/page")
        assert info.base_url == "https://example.com"

    def test_is_immutable(self):
        info = DomainInfo(scheme="https", netloc="example.com", path="/")
        with pytest.raises(AttributeError):
            info.scheme = "http"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# PreviewResult frozen dataclass
# ---------------------------------------------------------------------------


class TestPreviewResult:
    def test_is_frozen(self):
        from dataclasses import FrozenInstanceError
        r = PreviewResult(url="https://example.com", title="T")
        with pytest.raises(FrozenInstanceError):
            r.title = "other"  # type: ignore[misc]

    def test_is_success_true_with_title(self):
        assert PreviewResult(url="https://example.com", title="T").is_success is True

    def test_is_success_true_with_description(self):
        assert PreviewResult(url="https://example.com", description="D").is_success is True

    def test_is_success_true_with_favicon(self):
        assert PreviewResult(url="https://example.com", favicon="http://f.com/ico").is_success is True

    def test_is_success_false_when_all_none(self):
        assert PreviewResult(url="https://example.com").is_success is False

    def test_metadata_fields_excludes_url_and_error(self):
        r = PreviewResult(url="https://example.com", title="T", error="x")
        fields = r.metadata_fields
        assert "url" not in fields
        assert "error" not in fields
        assert "title" in fields


# ---------------------------------------------------------------------------
# FetchStats — Counter, defaultdict, deque, OrderedDict
# ---------------------------------------------------------------------------


class TestFetchStats:
    def _make_result(self, *, title: str | None = "T", error: str | None = None) -> PreviewResult:
        return PreviewResult(url="https://example.com", title=title, error=error)

    def test_records_success_outcome(self):
        stats = FetchStats()
        stats.record(self._make_result(), domain="example.com")
        assert stats.outcome_counter["success"] == 1

    def test_records_failure_outcome(self):
        stats = FetchStats()
        stats.record(
            self._make_result(title=None, error="HTTP 404"), domain="example.com"
        )
        assert stats.outcome_counter["failure"] == 1

    def test_records_circuit_open_outcome(self):
        stats = FetchStats()
        stats.record(
            self._make_result(title=None, error="Circuit breaker open for x"),
            domain="x",
        )
        assert stats.outcome_counter["circuit_open"] == 1

    def test_deque_bounded_by_window(self):
        stats = FetchStats(window=3)
        for _ in range(5):
            stats.record(self._make_result(), domain="example.com")
        assert len(stats.recent) == 3

    def test_failures_by_domain_uses_defaultdict(self):
        stats = FetchStats()
        stats.record(
            self._make_result(title=None, error="timeout"), domain="slow.com"
        )
        assert "slow.com" in stats.failures_by_domain
        assert stats.failures_by_domain["slow.com"] == ["timeout"]

    def test_summary_total_and_percentages(self):
        stats = FetchStats()
        for _ in range(3):
            stats.record(self._make_result(), domain="a.com")
        for _ in range(1):
            stats.record(self._make_result(title=None, error="x"), domain="a.com")
        s = stats.summary()
        assert s["total_fetches"] == 4
        success_row = next(r for r in s["outcomes"] if r["outcome"] == "success")
        assert success_row["percentage"] == 75.0

    def test_top_domains_uses_ordered_dict(self):
        stats = FetchStats()
        for _ in range(5):
            stats.record(self._make_result(), domain="top.com")
        for _ in range(2):
            stats.record(self._make_result(), domain="low.com")
        s = stats.summary()
        assert s["top_domains"][0][0] == "top.com"
