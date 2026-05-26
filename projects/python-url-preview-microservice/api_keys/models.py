"""API Key model — callers authenticate with a token, not user credentials.

Demonstrates:
- OOP: inheritance from TimeStampedModel
- @property decorators for computed fields
- secrets module for cryptographically secure token generation
- dataclass for structured metadata
- Counter/defaultdict for usage analytics
- Numerical operations: usage counting, rate-limit calculations
"""
from __future__ import annotations

import hashlib
import logging
import secrets
from collections import Counter
from dataclasses import dataclass

from core.models import TimeStampedModel
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)

_TOKEN_BYTES = 32  # 256-bit token → 64 hex chars


def _generate_token() -> str:
    """Return a cryptographically secure hex token."""
    return secrets.token_hex(_TOKEN_BYTES)


def _hash_token(raw: str) -> str:
    """SHA-256 hash of a token — only the hash is stored in the DB."""
    return hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Structured metadata value object (dataclass)
# ---------------------------------------------------------------------------


@dataclass
class APIKeyStats:
    """Usage statistics for a single API key.

    Demonstrates:
    - dataclass for structured data
    - Counter for frequency counting
    - defaultdict for grouping
    - Numerical operations: percentage computation, loops
    """

    key_id: int
    key_name: str
    total_requests: int
    requests_by_day: Counter[str]
    errors_by_type: dict[str, list[str]]

    @property
    def error_rate(self) -> float:
        """Fraction of requests that resulted in an error (0.0–1.0)."""
        if self.total_requests == 0:
            return 0.0
        total_errors = sum(len(v) for v in self.errors_by_type.values())
        # Numerical operation: division + round
        return round(total_errors / self.total_requests, 4)

    def daily_summary(self) -> list[dict]:
        """Return a sorted list of daily request counts."""
        # Loops + conditionals + numerical ops
        return [
            {
                "date": day,
                "count": count,
                "percentage": round(
                    count / self.total_requests * 100, 2
                ) if self.total_requests > 0 else 0.0,
            }
            for day, count in sorted(self.requests_by_day.items(), reverse=True)
        ]


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class APIKey(TimeStampedModel):
    """Stores a hashed API key for a named caller (e.g. url-shortener service).

    The raw token is NEVER stored — only its SHA-256 hash.
    The token is shown to the owner once at creation time only.
    """

    name = models.CharField(max_length=100, help_text="Friendly name for this key.")
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    request_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "token_hash"], name="apikey_active_hash_idx"),
        ]

    # ------------------------------------------------------------------
    # Class-level factory — returns (instance, raw_token)
    # ------------------------------------------------------------------

    @classmethod
    def create_key(cls, name: str) -> tuple[APIKey, str]:
        """Generate a new API key. Returns (saved instance, raw token).

        The raw token is only available here — store it securely.
        """
        raw = _generate_token()
        key = cls.objects.create(name=name, token_hash=_hash_token(raw))
        logger.info("API key created: id=%d name=%r", key.pk, name)
        return key, raw

    @classmethod
    def authenticate(cls, raw_token: str) -> APIKey | None:
        """Lookup a key by its token. Returns None if not found or revoked."""
        try:
            key = cls.objects.get(
                token_hash=_hash_token(raw_token),
                is_active=True,
                revoked_at__isnull=True,
            )
            # Update last_used_at without a full model save (atomic)
            cls.objects.filter(pk=key.pk).update(
                last_used_at=timezone.now(),
                request_count=models.F("request_count") + 1,
            )
            return key
        except cls.DoesNotExist:
            return None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_authenticated(self) -> bool:
        """Required by DRF's IsAuthenticated permission check."""
        return self.is_active and not self.is_revoked

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def display_name(self) -> str:
        return f"[{self.pk}] {self.name}"

    def revoke(self) -> None:
        """Permanently revoke this key."""
        self.revoked_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["revoked_at", "is_active", "updated_at"])
        logger.info("API key revoked: id=%d name=%r", self.pk, self.name)

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"APIKey(id={self.pk!r}, name={self.name!r}, active={self.is_active!r})"
