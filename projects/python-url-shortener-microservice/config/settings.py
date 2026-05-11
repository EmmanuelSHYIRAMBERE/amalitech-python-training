from datetime import timedelta
from pathlib import Path

from decouple import Csv, UndefinedValueError, config

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# .env validation — fail fast with a clear message if required vars are absent
# ---------------------------------------------------------------------------
try:
    SECRET_KEY: str = config("SECRET_KEY")
except UndefinedValueError:
    import os

    if os.environ.get("CI") or os.environ.get("PRE_COMMIT"):
        SECRET_KEY = "ci-dummy-secret-key-not-for-production"
    else:
        raise RuntimeError("SECRET_KEY is not set. Add it to your .env file.")

try:
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
except ValueError:
    DEBUG = False

ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", default="localhost", cast=Csv())

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    # Module 8: Celery result backend + beat scheduler
    "django_celery_results",
    "django_celery_beat",
    "core",
    "users",
    "shortener",
]

# Must be set before any migration that references the user model.
AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    # Module 8: structured error logging middleware
    "shortener.middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="urlshortener"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Module 8: Redis Cache Configuration
# ---------------------------------------------------------------------------
REDIS_URL: str = config("REDIS_URL", default="redis://redis:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Gracefully degrade if Redis is unavailable (don't crash the app).
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "urlshortener",
        # Default TTL for all cache keys: 1 hour.
        # Individual keys can override this with a specific timeout.
        "TIMEOUT": 3600,
    }
}

# Use Redis as the session backend too (optional, consistent with cache).
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ---------------------------------------------------------------------------
# Module 8: Celery Configuration
# ---------------------------------------------------------------------------
# All settings prefixed with CELERY_ are picked up by config/celery.py
# via app.config_from_object("django.conf:settings", namespace="CELERY").

CELERY_BROKER_URL: str = config("CELERY_BROKER_URL", default="redis://redis:6379/1")
CELERY_RESULT_BACKEND = "django-db"  # stores results in django_celery_results table
CELERY_CACHE_BACKEND = "default"

# Serialization — JSON is human-readable and safe (no pickle deserialization attacks).
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Timezone — must match Django's TIME_ZONE.
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Task routing — separate queues for different priority levels.
CELERY_TASK_ROUTES = {
    "shortener.tasks.track_click": {"queue": "default"},
    "shortener.tasks.cleanup_expired_urls": {"queue": "maintenance"},
}

# Retry policy — tasks retry up to 3 times with exponential backoff.
CELERY_TASK_MAX_RETRIES = 3

# Celery Beat — use the database scheduler so schedules survive restarts.
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ---------------------------------------------------------------------------
# DRF Configuration
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "login": "5/minute",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "shortener.middleware.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "URL Shortener API",
    "DESCRIPTION": (
        "Enterprise-Grade URL Shortener Microservice "
        "— Module 8: Advanced Optimization & Production Readiness"
    ),
    "VERSION": "4.0.0",
}

# ---------------------------------------------------------------------------
# Module 8: Structured JSON Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # Human-readable format for local development.
        "verbose": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # Structured JSON format for production log aggregation (Datadog, ELK, etc.).
        # Falls back to verbose if python-json-logger is not installed locally.
        "json": (
            {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            }
            if not DEBUG
            else {
                "format": "{asctime} [{levelname}] {name}: {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        ),
    },
    "filters": {
        # Only emit log records at WARNING level or above (for the security handler).
        "require_warning": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            # Use JSON in production (DEBUG=False), verbose locally.
            "formatter": "verbose" if DEBUG else "json",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "when": "midnight",
            "backupCount": 7,
            # Use json formatter in production, verbose locally.
            "formatter": "json" if not DEBUG else "verbose",
            "encoding": "utf-8",
        },
        # Separate handler for 500 errors and security warnings.
        "error_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "errors.log"),
            "when": "midnight",
            "backupCount": 30,
            "formatter": "json" if not DEBUG else "verbose",
            "encoding": "utf-8",
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "shortener": {
            "handlers": ["console", "file", "error_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "users": {
            "handlers": ["console", "file", "error_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # Celery task logging.
        "celery": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["console", "file", "error_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # Django internals — only warnings and above.
        "django.request": {
            "handlers": ["console", "file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
