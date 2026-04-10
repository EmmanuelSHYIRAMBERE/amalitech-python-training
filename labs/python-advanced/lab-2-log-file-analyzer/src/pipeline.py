"""Functional programming pipeline: map, filter, reduce aggregations."""

import functools
import operator
from collections.abc import Callable, Iterable, Iterator

from src.decorators import cache, log_call, timer
from src.parser import parse_lines


# ---------------------------------------------------------------------------
# map / filter helpers
# ---------------------------------------------------------------------------

def to_entries(lines: Iterable[str]) -> Iterator[dict]:
    """map() wrapper: parse raw lines into entry dicts."""
    return parse_lines(lines)


def by_status(entries: Iterable[dict], status: int) -> Iterator[dict]:
    """filter() wrapper: keep entries matching *status*."""
    return filter(lambda e: e["status"] == status, entries)


def by_status_range(entries: Iterable[dict], lo: int, hi: int) -> Iterator[dict]:
    """filter() wrapper: keep entries with status in [lo, hi]."""
    return filter(lambda e: lo <= e["status"] <= hi, entries)


def by_method(entries: Iterable[dict], method: str) -> Iterator[dict]:
    """filter() wrapper: keep entries matching HTTP *method*."""
    return filter(lambda e: e["method"] == method, entries)


def by_ip(entries: Iterable[dict], ip: str) -> Iterator[dict]:
    """filter() wrapper: keep entries from *ip*."""
    return filter(lambda e: e["ip"] == ip, entries)


# functools.partial specialisations
errors_only: Callable[[Iterable[dict]], Iterator[dict]] = functools.partial(
    by_status_range, lo=400, hi=599
)
server_errors: Callable[[Iterable[dict]], Iterator[dict]] = functools.partial(
    by_status_range, lo=500, hi=599
)
client_errors: Callable[[Iterable[dict]], Iterator[dict]] = functools.partial(
    by_status_range, lo=400, hi=499
)


# ---------------------------------------------------------------------------
# reduce aggregations
# ---------------------------------------------------------------------------

@timer
@log_call
def total_bytes(entries: Iterable[dict]) -> int:
    """reduce(): sum all response sizes."""
    return functools.reduce(lambda acc, e: acc + e["size"], entries, 0)


@timer
def count_by(entries: Iterable[dict], key: str) -> dict:
    """reduce(): count occurrences of each value for *key*."""
    def _acc(counts: dict, entry: dict) -> dict:
        counts[entry[key]] = counts.get(entry[key], 0) + 1
        return counts
    return functools.reduce(_acc, entries, {})


@timer
def top_urls(entries: Iterable[dict], n: int = 10) -> list[tuple[str, int]]:
    """Return the *n* most-requested clean URLs."""
    counts = count_by(entries, "url_clean")
    return sorted(counts.items(), key=operator.itemgetter(1), reverse=True)[:n]


@timer
def top_ips(entries: Iterable[dict], n: int = 10) -> list[tuple[str, int]]:
    """Return the *n* most active client IPs."""
    counts = count_by(entries, "ip")
    return sorted(counts.items(), key=operator.itemgetter(1), reverse=True)[:n]


# ---------------------------------------------------------------------------
# Cached status-code summary (demonstrates lru_cache on a pure function)
# ---------------------------------------------------------------------------

@cache(maxsize=128)
def status_label(code: int) -> str:
    """Return a human-readable label for an HTTP status *code*."""
    labels = {
        200: "OK", 201: "Created", 204: "No Content",
        301: "Moved Permanently", 302: "Found",
        400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
        404: "Not Found", 500: "Internal Server Error", 503: "Service Unavailable",
    }
    return labels.get(code, "Unknown")
