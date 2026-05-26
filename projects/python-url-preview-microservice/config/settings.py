"""Settings for the URL Preview Microservice.

This service has a SINGLE responsibility: fetch URL preview metadata
(title, description, favicon) and serve it over HTTP.

It authenticates callers with API keys — no user accounts needed.
"""

from __future__ import annotations

from pathlib import Path

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

ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", default="localhost", cast=Csv())

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    # Local apps
    "core",
    "api_keys",
    "preview",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "preview.middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database — owns its own schema (microservice isolation principle)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="urlpreview"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Redis — circuit breaker state + response cache
# ---------------------------------------------------------------------------
REDIS_URL: str = config("REDIS_URL", default="redis://redis:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "urlpreview",
        "TIMEOUT": 3600,
    }
}

# ---------------------------------------------------------------------------
# DRF — API key authentication by default, no session auth
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api_keys.authentication.APIKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "api_keys.throttles.APIKeyRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "api_key": config("API_KEY_RATE_LIMIT", default="1000") + "/day",
    },
    "EXCEPTION_HANDLER": "preview.middleware.custom_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "URL Preview Microservice",
    "DESCRIPTION": (
        "A standalone microservice that fetches title, description, and favicon "
        "from any URL. Authenticated via API keys. Implements circuit breaker, "
        "exponential-backoff retry, and structured JSON logging.\n\n"
        "**How to authenticate:**\n"
        "1. Use `POST /api/v1/keys/` to create an API key\n"
        "2. Copy the `token` from the response\n"
        "3. Click **Authorize** and enter: `Bearer <your-token>`"
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Adds the Authorize 🔒 button + security schemes to Swagger UI
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "Token",
                "description": "Enter your API token (from POST /api/v1/keys/)",
            },
        }
    },
    "SECURITY": [{"BearerAuth": []}],
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
}

# ---------------------------------------------------------------------------
# CORS — allow the URL shortener service to call this API from its backend
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS: list[str] = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:8000,http://127.0.0.1:8000",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "x-api-key",
]

# ---------------------------------------------------------------------------
# Structured JSON Logging — always JSON for errors.log
# ---------------------------------------------------------------------------
LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")

try:
    import pythonjsonlogger.jsonlogger  # noqa: F401

    _json_available = True
except ImportError:
    _json_available = False

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": (
            {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            }
            if _json_available
            else {
                "format": "{asctime} [{levelname}] {name}: {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        ),
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "json",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "when": "midnight",
            "backupCount": 7,
            "formatter": "json" if not DEBUG else "verbose",
            "encoding": "utf-8",
        },
        # Always JSON — all 500 errors and security warnings go here
        "error_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "errors.log"),
            "when": "midnight",
            "backupCount": 30,
            "formatter": "json",
            "encoding": "utf-8",
            "level": "ERROR",
        },
    },
    "root": {"handlers": ["console", "file"], "level": LOG_LEVEL},
    "loggers": {
        "preview": {
            "handlers": ["console", "file", "error_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "api_keys": {
            "handlers": ["console", "file", "error_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
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
    },
}
