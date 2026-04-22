<div align="center">
  <img src="https://amalitech.com/wp-content/uploads/elementor/thumbs/cropped-Logo-AmaliTech-2024_AmaliTech-1-1-qwx787mrcfwkgtwtxyaig0bixrwoxjaylsrbwor7ek.png" alt="AmaliTech Logo" width="280"/>
</div>
<br/>

# URL Shortener Microservice — Module 5

> **Phase 1 Foundation** · Django 5.0+ · DRF · PostgreSQL 15 · Docker

![CI](https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training/actions/workflows/python-url-shortener-mod5.yml/badge.svg)

---

## About

|             |                                                         |
| ----------- | ------------------------------------------------------- |
| **Trainee** | Emmanuel SHYIRAMBERE                                    |
| **Module**  | Module 5 — Django REST Framework & Microservices        |
| **Stack**   | Python 3.11 · Django 5.0 · DRF · PostgreSQL 15 · Docker |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Docker Compose                    │
│                                                     │
│  ┌──────────────────┐      ┌─────────────────────┐  │
│  │   web (Django)   │─────▶│  db (PostgreSQL 15) │  │
│  │   :8000          │      │  :5435              │  │
│  └──────────────────┘      └─────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Project Structure

```
url-shortener-microservice/
├── config/
│   ├── settings.py       # python-decouple config + LOGGING
│   ├── urls.py           # root router + Swagger
│   └── wsgi.py
├── shortener/
│   ├── models.py         # URL model + secrets-based short_code generator
│   ├── serializers.py    # DRF serializers with full type annotations
│   ├── views.py          # POST create + GET redirect + structured logging
│   ├── urls.py           # /<short_code>/ redirect route
│   └── migrations/
├── core/
│   ├── models.py         # TimeStampedModel abstract base
│   └── views.py          # GET /health/ endpoint
├── api/
│   └── urls.py           # /api/v1/ versioned routes
├── tests/
│   ├── conftest.py       # shared fixtures (api_client, created_url)
│   ├── test_models.py    # generate_short_code + URL model
│   ├── test_serializers.py
│   ├── test_views.py     # POST /api/v1/urls/ + GET /<short_code>/
│   └── test_health.py
├── logs/                 # rotating log files (git-ignored)
├── Dockerfile            # multi-stage Alpine build + non-root user
├── .dockerignore
├── docker-compose.yml
├── .env.example
├── .pre-commit-config.yaml  # black + ruff + mypy
├── pyproject.toml        # ruff + mypy + pytest + coverage config
└── requirements.txt
```

---

## Setup

### 1. Clone and navigate

```bash
git clone https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training.git
cd projects/python-url-shortener-microservice
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` — required variables:

| Variable        | Description                                   | Example               |
| --------------- | --------------------------------------------- | --------------------- |
| `SECRET_KEY`    | Django secret key                             | `django-insecure-...` |
| `DEBUG`         | Debug mode                                    | `True`                |
| `ALLOWED_HOSTS` | Comma-separated hosts                         | `localhost,127.0.0.1` |
| `DB_NAME`       | PostgreSQL database name                      | `urlshortener`        |
| `DB_USER`       | PostgreSQL user                               | `postgres`            |
| `DB_PASSWORD`   | PostgreSQL password                           | `admin321`            |
| `DB_HOST`       | DB host (`db` in Docker, `localhost` locally) | `localhost`           |
| `DB_PORT`       | DB port (mapped port locally)                 | `5435`                |
| `LOG_LEVEL`     | Logging level                                 | `INFO`                |

> **Local vs Docker:** When running outside Docker set `DB_HOST=localhost` and `DB_PORT=5435`.
> Inside Docker Compose the service name `db` and port `5432` are used automatically.

### 3. Run with Docker (recommended)

```bash
docker compose up --build
# Service is live at http://localhost:8000
```

### 4. Run locally (without Docker)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
python manage.py makemigrations shortener
python manage.py migrate --noinput
python manage.py runserver
```

### 5. Install pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files    # verify all hooks pass
```

Hooks: **black** (formatting) · **ruff** (linting) · **mypy** (strict type checking)

---

## API Endpoints

| Method | Endpoint         | Description                                        |
| ------ | ---------------- | -------------------------------------------------- |
| `POST` | `/api/v1/urls/`  | Shorten a URL → returns `short_code` + `short_url` |
| `GET`  | `/<short_code>/` | Redirect to original URL (HTTP 302)                |
| `GET`  | `/health/`       | Health check — DB connectivity                     |
| `GET`  | `/api/docs/`     | Swagger UI (drf-spectacular)                       |
| `GET`  | `/api/schema/`   | OpenAPI schema (JSON)                              |

---

## Usage Examples

### Shorten a URL

```bash
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.example.com/very/long/path"}'
```

Response `201 Created`:

```json
{
  "short_code": "aB3xYz",
  "original_url": "https://www.example.com/very/long/path",
  "short_url": "http://localhost:8000/aB3xYz/",
  "created_at": "2025-01-01T12:00:00Z"
}
```

### Follow a redirect

```bash
curl -L http://localhost:8000/aB3xYz/
# → HTTP 302 → https://www.example.com/very/long/path
```

### Health check

```bash
curl http://localhost:8000/health/
# {"status": "ok", "db": "reachable"}
```

### Invalid URL — 400 response

```bash
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"original_url": "not-a-url"}'
# {"original_url": ["Enter a valid URL."]}
```

---

## Running Tests

```bash
# Full suite
pytest

# With coverage report
coverage run -m pytest
coverage report

# HTML coverage report
coverage html
start htmlcov/index.html      # Windows
open htmlcov/index.html       # macOS
```

---

## Logging

Logs are written to both stdout and `logs/app.log` (rotated daily, 7-day retention).

```
2025-01-01 12:00:00 [INFO] shortener.views: POST /api/v1/urls/ — created short_code='aB3xYz' original_url='https://...'
2025-01-01 12:00:01 [INFO] shortener.views: GET /aB3xYz/ — redirecting to 'https://...'
```

Control the log level via `.env`:

```
LOG_LEVEL=DEBUG   # verbose — includes short_code generation
LOG_LEVEL=INFO    # default — API requests only
LOG_LEVEL=WARNING # quiet — errors only
```

---

## Type Checking

```bash
mypy config/ shortener/ api/ core/
```

Configured in `pyproject.toml` with `strict = true` and `django-stubs` + `djangorestframework-stubs`.

---

## Module 5 Checklist

- [x] Modular Django project structure (`config`, `shortener`, `api`, `core` apps)
- [x] `python-decouple` for environment-based configuration with runtime validation
- [x] `URL` model with `original_url` (max 2048 chars) + `short_code` (indexed, unique)
- [x] Cryptographically secure short code generator (`secrets` module)
- [x] `POST /api/v1/urls/` — create short link with DRF serializer validation
- [x] `GET /<short_code>/` — HTTP 302 redirect
- [x] `GET /health/` — DB connectivity health check
- [x] Full type annotations on all views, serializers, and models
- [x] Structured logging to stdout + rotating file (`logs/app.log`)
- [x] Full pytest suite — models, serializers, views, health check
- [x] Multi-stage Alpine `Dockerfile` with non-root user + health check
- [x] `.dockerignore` to minimise build context
- [x] `docker-compose.yml` — Django + PostgreSQL 15 with health check
- [x] `drf-spectacular` Swagger/OpenAPI docs at `/api/docs/`
- [x] API versioning at `/api/v1/`
- [x] Pre-commit hooks: black + ruff + mypy
- [x] CI pipeline: lint/mypy → docker-build → django-check → pytest/coverage

---

_Python 3.11+ · Django 5.0 · DRF · PostgreSQL 15 · AmaliTech Training Program_
