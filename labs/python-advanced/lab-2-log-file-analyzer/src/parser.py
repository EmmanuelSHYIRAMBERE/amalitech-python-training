"""Parse raw Apache/Nginx log lines into structured dictionaries."""

import datetime
from typing import Iterator

from src.patterns import LOG_LINE, MULTI_SLASH, QUERY_STRIP, TIMESTAMP

_MONTH = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def _parse_timestamp(raw: str) -> datetime.datetime:
    """Convert Apache timestamp string to a datetime object."""
    m = TIMESTAMP.match(raw)
    if not m:
        raise ValueError(f"Unrecognised timestamp: {raw!r}")
    return datetime.datetime(
        int(m["year"]), _MONTH[m["month"]], int(m["day"]),
        int(m["hour"]), int(m["minute"]), int(m["second"]),
    )


def parse_line(line: str) -> dict | None:
    """Parse a single log line.

    Returns a structured dict or None if the line does not match.

    Keys: ip, timestamp (datetime), method, url, url_clean, protocol,
          status (int), size (int), referrer, agent, hour (int).
    """
    m = LOG_LINE.match(line.strip())
    if not m:
        return None
    g = m.groupdict()
    ts = _parse_timestamp(g["timestamp"])
    url_clean = MULTI_SLASH.sub("/", QUERY_STRIP.sub("", g["url"]))
    return {
        "ip": g["ip"],
        "timestamp": ts,
        "method": g["method"],
        "url": g["url"],
        "url_clean": url_clean,
        "protocol": g["protocol"],
        "status": int(g["status"]),
        "size": int(g["size"]) if g["size"] != "-" else 0,
        "referrer": g["referrer"],
        "agent": g["agent"],
        "hour": ts.hour,
    }


def parse_lines(lines: Iterator[str]) -> Iterator[dict]:
    """Yield parsed dicts for every successfully matched line."""
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            yield entry
