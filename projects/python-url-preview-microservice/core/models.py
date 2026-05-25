"""Abstract base model providing audit timestamps."""
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base — all domain models get created_at / updated_at."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
