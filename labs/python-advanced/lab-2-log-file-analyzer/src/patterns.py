"""Compiled regex patterns for Apache/Nginx combined log format.

Pattern anatomy (named groups):
  ip        – client IPv4 address
  timestamp – raw datetime string inside brackets
  method    – HTTP verb
  url       – request path (may include query string)
  protocol  – HTTP version
  status    – 3-digit response code
  size      – response body bytes (or 0/-)
  referrer  – Referer header value
  agent     – User-Agent header value

Validation helpers:
  IP_VALIDATE   – strict IPv4 dotted-quad
  EMAIL_VALIDATE – RFC-5321-ish email
  URL_VALIDATE  – http/https URL
"""

import re

# ---------------------------------------------------------------------------
# Primary log-line pattern (Apache Combined Log Format)
# ---------------------------------------------------------------------------
LOG_LINE = re.compile(
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})"   # client IP
    r" \S+ \S+ "                           # ident & auth (ignored)
    r"\[(?P<timestamp>[^\]]+)\]"           # [timestamp]
    r' "(?P<method>[A-Z]+) '              # "METHOD
    r"(?P<url>\S+) "                       # /path
    r'(?P<protocol>HTTP/\d\.\d)"'         # HTTP/1.1"
    r" (?P<status>\d{3})"                  # status code
    r" (?P<size>\d+|-)"                    # bytes sent
    r' "(?P<referrer>[^"]*)"'             # "Referer"
    r' "(?P<agent>[^"]*)"'                # "User-Agent"
)

# ---------------------------------------------------------------------------
# Timestamp pattern – extracts components from Apache timestamp
# e.g. "01/Jan/2024:00:00:00 +0000"
# ---------------------------------------------------------------------------
TIMESTAMP = re.compile(
    r"(?P<day>\d{2})/(?P<month>[A-Za-z]{3})/(?P<year>\d{4})"
    r":(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r" (?P<tz>[+-]\d{4})"
)

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
IP_VALIDATE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)

EMAIL_VALIDATE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

URL_VALIDATE = re.compile(
    r"^https?://[^\s/$.?#].[^\s]*$"
)

# ---------------------------------------------------------------------------
# Cleaning helpers
# ---------------------------------------------------------------------------
# Strip query strings from URLs for grouping
QUERY_STRIP = re.compile(r"\?.*$")

# Normalise repeated slashes
MULTI_SLASH = re.compile(r"/{2,}")
