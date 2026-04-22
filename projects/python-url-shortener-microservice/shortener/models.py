"""Django models for the shortener app."""

from django.db import models

from core.models import TimeStampedModel


class URL(TimeStampedModel):
    # max_length=2048 covers the practical maximum URL length (RFC 7230).
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.short_code} → {self.original_url}"
