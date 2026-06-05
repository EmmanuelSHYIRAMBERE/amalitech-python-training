"""Test settings for the URL Shortener Microservice.

Overrides DATABASES and CACHES so the full test suite runs against
SQLite in-memory and LocMemCache — no PostgreSQL or Redis needed.

Loaded by pytest via pyproject.toml:
    [tool.pytest.ini_options]
    DJANGO_SETTINGS_MODULE = "config.test_settings"
"""

import os

# Set CI flag before importing base settings so the SECRET_KEY guard
# does not raise when running pytest locally without a .env file.
os.environ.setdefault("CI", "true")

from config.settings import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Database — SQLite in-memory; no Docker required for tests
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ---------------------------------------------------------------------------
# Cache — local memory; no Redis required for tests
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ---------------------------------------------------------------------------
# Celery — run tasks eagerly and synchronously in tests
# ---------------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
