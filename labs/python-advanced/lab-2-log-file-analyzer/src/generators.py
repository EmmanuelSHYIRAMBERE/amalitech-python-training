"""Memory-efficient generators and itertools utilities for log processing."""

import itertools
import operator
from collections.abc import Generator, Iterable, Iterator
from pathlib import Path
from typing import Any


def read_log_lines(path: Path) -> Generator[str, None, None]:
    """Yield raw lines from *path* one at a time (O(1) memory)."""
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            yield line


def batch(iterable: Iterable[dict], size: int) -> Iterator[list[dict]]:
    """Yield successive *size*-length chunks from *iterable*."""
    it = iter(iterable)
    while chunk := list(itertools.islice(it, size)):
        yield chunk


def chain_logs(*paths: Path) -> Generator[str, None, None]:
    """Yield lines from multiple log files in sequence."""
    yield from itertools.chain.from_iterable(read_log_lines(p) for p in paths)


def takewhile_date(entries: Iterable[dict], start: str, end: str) -> Iterator[dict]:
    """Yield entries whose date string (YYYY-MM-DD) falls within [start, end].

    Uses itertools.takewhile to stop as soon as the timestamp exceeds *end*
    (assumes entries are chronologically ordered).
    """
    in_range = (
        e for e in entries
        if e["timestamp"].strftime("%Y-%m-%d") >= start
    )
    return itertools.takewhile(
        lambda e: e["timestamp"].strftime("%Y-%m-%d") <= end,
        in_range,
    )


def group_by(entries: Iterable[dict], key: str) -> Iterator[tuple[Any, Iterator[dict]]]:
    """Group *entries* by *key* using itertools.groupby.

    Entries must be pre-sorted by *key* for groupby to work correctly.
    """
    keyfn = operator.itemgetter(key)
    yield from itertools.groupby(sorted(entries, key=keyfn), key=keyfn)
