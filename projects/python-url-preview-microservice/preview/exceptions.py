"""Custom exception hierarchy for the preview domain.

Demonstrates:
- Structured exception hierarchy (OOP, open/closed principle)
- Each subclass carries domain-specific context
"""

from __future__ import annotations


class PreviewError(Exception):
    """Base class for all preview-domain errors."""


class FetchError(PreviewError):
    """Raised when an HTTP fetch fails after all retries."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Fetch failed for {url!r}: {reason}")


class CircuitOpenError(PreviewError):
    """Raised when the circuit breaker is open for a domain."""

    def __init__(self, domain: str) -> None:
        self.domain = domain
        super().__init__(f"Circuit breaker is open for domain {domain!r}")


class ParseError(PreviewError):
    """Raised when HTML parsing produces no usable metadata."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"No metadata could be parsed from {url!r}")
