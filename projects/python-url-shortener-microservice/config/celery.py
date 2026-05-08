"""Celery application configuration for the URL Shortener Microservice.

This module creates the Celery app instance and configures it from Django settings.
It must be imported in config/__init__.py so Django loads it on startup.

Usage::

    # Start a worker
    celery -A config worker --loglevel=info

    # Start the beat scheduler (periodic tasks)
    celery -A config beat --loglevel=info \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler

    # Inspect active tasks
    celery -A config inspect active
"""

import os

from celery import Celery
from celery.schedules import crontab

# Tell Celery which Django settings module to use.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Load all CELERY_* settings from Django's settings.py.
# namespace="CELERY" means every Celery setting must be prefixed with CELERY_.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all INSTALLED_APPS.
# Celery looks for a tasks.py file in each app directory.
app.autodiscover_tasks()

# ---------------------------------------------------------------------------
# Periodic Tasks (Celery Beat)
# ---------------------------------------------------------------------------
# These are defined here as a fallback. In production, use the Django admin
# or DatabaseScheduler to manage schedules without redeploying.

app.conf.beat_schedule = {
    # Run every night at 02:00 UTC to archive expired URLs.
    "cleanup-expired-urls-nightly": {
        "task": "shortener.tasks.cleanup_expired_urls",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "maintenance"},
    },
}
