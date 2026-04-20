import random
import string
from django.db import models


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not URL.objects.filter(short_code=code).exists():
            return code


class URL(models.Model):
    original_url = models.URLField()
    short_code = models.CharField(max_length=10, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.short_code} → {self.original_url}"
