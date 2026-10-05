"""Settings for the Photo Uploader service (Django/DRF rewrite of the
Node/Express app). No auth, no Redis, no Celery -- single domain app.
"""

from __future__ import annotations

import json
from pathlib import Path

import boto3
from decouple import Csv, UndefinedValueError, config

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
try:
    SECRET_KEY: str = config("SECRET_KEY")
except UndefinedValueError:
    import os

    if (
        os.environ.get("CI")
        or os.environ.get("PRE_COMMIT")
        or os.environ.get("PYTEST_CURRENT_TEST")
        or "pytest" in os.environ.get("_", "")
    ):
        SECRET_KEY = "ci-dummy-secret-key-not-for-production"
    else:
        raise RuntimeError("SECRET_KEY is not set. Add it to your .env file.") from None

try:
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
except ValueError:
    DEBUG = False

# The Node app never validated the Host header -- default "*" preserves
# current behavior; tighten later if desired.
ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", default="*", cast=Csv())

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    "core",
    "photos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database -- replicates src/db/pool.ts's Secrets-Manager/SSL conditional.
# Node did this lazily on first pool use; Django needs it eagerly here
# since DATABASES is built at settings-import time.
# ---------------------------------------------------------------------------
AWS_REGION: str = config("AWS_REGION", default="eu-north-1")
DB_SECRET_ARN: str = config("DB_SECRET_ARN", default="")


def _resolve_db_password() -> tuple[str, bool]:
    """Returns (password, use_ssl) exactly like pool.ts's resolvePassword()
    plus the useSsl boolean derived from whether DB_SECRET_ARN is set.
    """
    if not DB_SECRET_ARN:
        # Local dev / no-secret path -- plain DB_PASSWORD env var, no SSL.
        return config("DB_PASSWORD", default=""), False

    # Production/ECS path -- fetch from Secrets Manager, force SSL.
    client = boto3.client("secretsmanager", region_name=AWS_REGION)
    response = client.get_secret_value(SecretId=DB_SECRET_ARN)
    secret = json.loads(response.get("SecretString") or "{}")
    return secret.get("password", ""), True


_DB_PASSWORD, _DB_USE_SSL = _resolve_db_password()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="photouploader"),
        "USER": config("DB_USER", default="photoapp"),
        "PASSWORD": _DB_PASSWORD,
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        # sslmode="require" encrypts the connection but does not verify the
        # server certificate against a CA bundle -- the psycopg2/libpq
        # equivalent of Node's ssl:{rejectUnauthorized:false}. Omitted
        # entirely (not "disable") when DB_SECRET_ARN is unset, matching
        # pool.ts's ssl:false for local/non-RDS Postgres.
        "OPTIONS": {"sslmode": "require"} if _DB_USE_SSL else {},
    }
}

# photos.Photo declares its own UUIDField primary_key explicitly -- this
# default only applies to any future model that doesn't set one.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# S3 / CloudFront -- consumed by photos/services.py
# ---------------------------------------------------------------------------
PHOTOS_BUCKET: str = config("PHOTOS_BUCKET", default="")
CLOUDFRONT_DOMAIN: str = config("CLOUDFRONT_DOMAIN", default="")

# ---------------------------------------------------------------------------
# File upload -- keep uploads in memory (mirrors multer's memoryStorage,
# no temp files on disk). Default Django threshold is 2.5MB; the app's
# validated max is 10MB, so raise this above that limit.
# ---------------------------------------------------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # covers non-file POST body too

# ---------------------------------------------------------------------------
# DRF
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.JSONParser",
    ],
    "EXCEPTION_HANDLER": "photos.exceptions.custom_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Photo Uploader API",
    "DESCRIPTION": "Photo gallery: upload to S3, serve via CloudFront, metadata in RDS.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------------------------------------------------------------------
# CORS -- matches Node's cors({origin: '*'})
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
