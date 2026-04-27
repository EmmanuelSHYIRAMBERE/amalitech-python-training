"""Custom User model for the URL Shortener.

Extends AbstractUser to add premium tier tracking.
AUTH_USER_MODEL must point here before any migrations are run.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user with premium tier support.

    Inherits all standard Django auth fields (username, email, password,
    first_name, last_name, is_staff, is_active, date_joined, etc.) from
    AbstractUser and adds application-specific fields.
    """

    class Tier(models.TextChoices):
        FREE = "Free", "Free"
        PREMIUM = "Premium", "Premium"
        ADMIN = "Admin", "Admin"

    # Override email to enforce uniqueness — AbstractUser allows duplicates.
    email = models.EmailField(unique=True)

    is_premium = models.BooleanField(
        default=False,
        help_text="Designates whether this user has premium access.",
    )
    tier = models.CharField(
        max_length=10,
        choices=Tier.choices,
        default=Tier.FREE,
    )

    def __str__(self) -> str:
        return f"{self.username} ({self.tier})"
