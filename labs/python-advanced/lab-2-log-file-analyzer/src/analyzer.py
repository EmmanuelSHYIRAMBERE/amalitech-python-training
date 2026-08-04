"""Orchestrate the full analysis pipeline and produce a report dict."""

import json
from pathlib import Path

from src.decorators import timer
from src.generators import batch, group_by, read_log_lines
from src.parser import parse_lines
from src.pipeline import (
    client_errors,
    count_by,
    errors_only,
    server_errors,
    to_entries,
    top_ips,
    top_urls,
    total_bytes,
)


def _load_entries(path: Path) -> list[dict]:
    """Read and parse all entries from *path* into a list."""
    return list(to_entries(read_log_lines(path)))


@timer
def analyze(path: Path) -> dict:
    """Run the full analysis pipeline on *path* and return a report dict."""
    entries = _load_entries(path)

    status_counts = count_by(iter(entries), "status")
    method_counts = count_by(iter(entries), "method")
    hourly_counts = count_by(iter(entries), "hour")

    # itertools.groupby: requests per status group
    status_groups = {
        str(k): sum(1 for _ in grp)
        for k, grp in group_by(entries, "status")
    }

    # itertools.groupby: requests per hour
    hourly_groups = {
        str(k): sum(1 for _ in grp)
        for k, grp in group_by(entries, "hour")
    }

    error_entries = list(errors_only(iter(entries)))
    server_err_entries = list(server_errors(iter(entries)))
    client_err_entries = list(client_errors(iter(entries)))

    return {
        "total_requests": len(entries),
        "total_bytes": total_bytes(iter(entries)),
        "status_counts": {str(k): v for k, v in sorted(status_counts.items())},
        "method_counts": method_counts,
        "hourly_traffic": {str(k): v for k, v in sorted(hourly_counts.items())},
        "top_urls": top_urls(iter(entries), n=10),
        "top_ips": top_ips(iter(entries), n=10),
        "error_count": len(error_entries),
        "server_error_count": len(server_err_entries),
        "client_error_count": len(client_err_entries),
        "error_rate_pct": round(len(error_entries) / max(len(entries), 1) * 100, 2),
    }


@timer
def save_report(report: dict, out: Path) -> None:
    """Serialise *report* to JSON at *out*."""
    out.parent.mkdir(parents=True, exist_ok=True)
    # top_urls / top_ips are lists of tuples – convert for JSON
    serialisable = {
        **report,
        "top_urls": [{"url": u, "count": c} for u, c in report["top_urls"]],
        "top_ips": [{"ip": ip, "count": c} for ip, c in report["top_ips"]],
    }
    out.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")


def batch_demo(path: Path, batch_size: int = 100) -> None:
    """Print batch counts to demonstrate generator-based batching."""
    entries = to_entries(read_log_lines(path))
    for i, chunk in enumerate(batch(entries, batch_size), 1):
        print(f"  Batch {i:>3}: {len(chunk)} entries")
