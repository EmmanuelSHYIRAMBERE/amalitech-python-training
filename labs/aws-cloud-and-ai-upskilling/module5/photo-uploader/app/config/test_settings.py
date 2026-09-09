"""Test settings -- SQLite in-memory, no AWS calls."""

import os

os.environ.setdefault("DB_SECRET_ARN", "")  # force local-password path, no boto3 call
os.environ.setdefault("PHOTOS_BUCKET", "test-bucket")
os.environ.setdefault("CLOUDFRONT_DOMAIN", "test.cloudfront.net")
os.environ.setdefault("CI", "true")  # settings.py's SECRET_KEY fallback needs this

from config.settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
