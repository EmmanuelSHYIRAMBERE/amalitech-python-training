import logging
import secrets
import string

from django.db import models

from core.models import TimeStampedModel

logger = logging.getLogger(__name__)


def generate_short_code(length: int = 6) -> str:
    """Generate a cryptographically secure, collision-free alphanumeric short code.

    Uses ``secrets.choice`` instead of ``random.choices`` so the output is
    suitable for use as a public-facing token.

    Args:
        length: Number of characters in the generated code. Defaults to 6.

    Returns:
        A unique alphanumeric string of the requested length.
    """
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(secrets.choice(chars) for _ in range(length))
        if not URL.objects.filter(short_code=code).exists():
            logger.debug("Generated short_code=%r", code)
            return code


class URL(TimeStampedModel):
    # max_length=2048 covers the practical maximum URL length (RFC 7230).
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.short_code} → {self.original_url}"
