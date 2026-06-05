"""Management command: ensure_service_api_key.

Creates a fixed API key for the URL shortener service if one does not already
exist with the given name.  Called during container startup so the preview
service is always bootstrapped with a known key — no manual step required
after a database reset.

Usage (in docker-compose.yml command):
    python manage.py ensure_service_api_key

Environment variables read:
    PREVIEW_SERVICE_API_KEY_NAME  — display name stored on the APIKey record
                                    (default: "url-shortener")
    PREVIEW_SERVICE_API_KEY_TOKEN — 64-hex-char raw token to seed.
                                    If blank a random token is generated and
                                    printed to stdout so it can be captured by
                                    a startup script.
"""

from __future__ import annotations

import hashlib
import os

from django.core.management.base import BaseCommand

from api_keys.models import APIKey


class Command(BaseCommand):
    help = "Ensure a service API key exists; create it if not."

    def handle(self, *args: object, **options: object) -> None:
        name = os.environ.get("PREVIEW_SERVICE_API_KEY_NAME", "url-shortener")
        raw_token = os.environ.get("PREVIEW_SERVICE_API_KEY_TOKEN", "")

        # If a fixed token is supplied, check whether it already exists.
        if raw_token:
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            if APIKey.objects.filter(token_hash=token_hash, is_active=True).exists():
                self.stdout.write(
                    self.style.SUCCESS(
                        f"API key '{name}' already exists — no action taken."
                    )
                )
                return
            # Create with the supplied token.
            key = APIKey(name=name, token_hash=token_hash, is_active=True)
            key.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"API key '{name}' created with supplied token."
                )
            )
        else:
            # Generate a fresh random token and print it so the caller can
            # capture it (e.g. via docker compose exec or a startup script).
            key, raw_token = APIKey.create_key(name=name)
            self.stdout.write(f"PREVIEW_SERVICE_API_KEY_TOKEN={raw_token}")
            self.stdout.write(
                self.style.SUCCESS(f"API key '{name}' created (id={key.pk}).")
            )
