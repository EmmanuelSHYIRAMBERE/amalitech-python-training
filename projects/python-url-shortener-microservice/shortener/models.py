import random
import string

from django.db import models

from core.models import TimeStampedModel


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not URL.objects.filter(short_code=code).exists():
            return code


class URL(TimeStampedModel):
    original_url = models.URLField()
    short_code = models.CharField(max_length=10, unique=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.short_code} → {self.original_url}"
