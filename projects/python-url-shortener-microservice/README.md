<div align="center">
  <img src="https://amalitech.com/wp-content/uploads/elementor/thumbs/cropped-Logo-AmaliTech-2024_AmaliTech-1-1-qwx787mrcfwkgtwtxyaig0bixrwoxjaylsrbwor7ek.png" alt="AmaliTech Logo" width="280"/>
</div>
<br/>

# URL Shortener Microservice

> **Enterprise-Grade URL Shortener** · Django 5.0+ · DRF · PostgreSQL 15 · Docker

![CI Mod 5](https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training/actions/workflows/python-url-shortener-mod5.yml/badge.svg)
![CI Mod 6](https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training/actions/workflows/python-url-shortener-mod6.yml/badge.svg)

---

## About

|                |                                                              |
| -------------- | ------------------------------------------------------------ |
| **Trainee**    | Emmanuel SHYIRAMBERE                                         |
| **Modules**    | Module 5 — Foundation & Containerization · Module 6 — ORM & Data Access Layer |
| **Stack**      | Python 3.11 · Django 5.0 · DRF · PostgreSQL 15 · Docker     |
| **Tests**      | 123 passing                                                  |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
│                                                              │
│  ┌───────────────────────┐      ┌──────────────────────────┐ │
│  │    web (Django 5)     │─────▶│   db (PostgreSQL 15)     │ │
│  │    gunicorn :8000     │      │   :5435 (host-mapped)    │ │
│  └───────────────────────┘      └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

Request flow:
  POST /api/v1/urls/          →  URLCreateView  →  URL.objects.create()
  GET  /<short_code>/         →  RedirectView   →  Click.objects.create()  →  302
  GET  /api/v1/analytics/<>/  →  URLAnalyticsView  →  annotate(Count)
  GET  /health/               →  HealthCheckView   →  connection.ensure_connection()
  GET  /api/docs/             →  Swagger UI (drf-spectacular)
```

---

## Project Structure

```
url-shortener-microservice/
├── config/
│   ├── settings.py          # python-decouple config, AUTH_USER_MODEL, LOGGING
│   ├── urls.py              # root router + Swagger endpoints
│   ├── wsgi.py              # gunicorn entry point
│   └── asgi.py              # uvicorn entry point (available)
│
├── users/                   # Mod 6 — custom User model
│   ├── models.py            # User(AbstractUser) + is_premium + tier
│   ├── apps.py
│   └── migrations/
│       └── 0001_initial.py
│
├── shortener/
│   ├── models.py            # URL + Tag + Click + URLQuerySet + URLManager
│   ├── generators.py        # BaseShortCodeGenerator (ABC) + SecureShortCodeGenerator
│   ├── protocols.py         # ShortCodeGenerator Protocol (PEP 544)
│   ├── schemas.py           # ShortenRequest, ShortenResult, ClickResult dataclasses
│   ├── serializers.py       # URLCreate/Response/Analytics + Tag + Click serializers
│   ├── validators.py        # compiled regex validators (short_code + URL scheme)
│   ├── views.py             # URLCreateView + RedirectView + URLAnalyticsView
│   ├── urls.py              # /<short_code>/ redirect route
│   └── migrations/
│       ├── 0001_initial.py
│       ├── 0002_mod6_schema.py   # Tag, Click, all new URL fields, indexes
│       └── 0003_seed_default_tags.py  # data migration — 10 default tags
│
├── core/
│   ├── models.py            # TimeStampedModel abstract base (created_at, updated_at)
│   ├── views.py             # GET /health/ — DB connectivity check
│   └── urls.py
│
├── api/
│   └── urls.py              # /api/v1/ versioned routes (urls + analytics)
│
├── tests/
│   ├── conftest.py          # fixtures: api_client, user, premium_user, tags, created_url
│   ├── test_health.py       # 5 tests — health check endpoint
│   ├── test_models.py       # 39 tests — User, Tag, URL, Click, URLManager, aggregation
│   ├── test_serializers.py  # 21 tests — all serializers including analytics
│   └── test_views.py        # 31 tests — all views including Mod 6 behaviour
│
├── docs-explanation/        # deep-dive explanation docs (one file per topic)
├── logs/                    # rotating log files (git-ignored)
├── Dockerfile               # multi-stage Alpine build + non-root user
├── .dockerignore
├── docker-compose.yml
├── .env.example
├── .pre-commit-config.yaml  # ruff + black + mypy hooks
├── pyproject.toml           # ruff + mypy + pytest + coverage config
└── requirements.txt
```

---

## Database Schema

```
┌──────────────────┐         ┌──────────────────┐
│      users_user  │         │   shortener_tag  │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ username         │         │ name (unique)    │
│ email (unique)   │         └────────┬─────────┘
│ is_premium       │                  │ M2M
│ tier             │                  │
└────────┬─────────┘         ┌────────▼──────────────────┐
         │ FK (owner)        │      shortener_url         │
         │                   ├───────────────────────────┤
         └──────────────────▶│ id (PK)                   │
                             │ original_url              │
                             │ short_code (unique, idx)  │
                             │ custom_alias (unique)     │
                             │ owner FK → users_user     │
                             │ click_count               │
                             │ is_active (idx)           │
                             │ expires_at (idx)          │
                             │ title / description       │
                             │ favicon                   │
                             │ created_at (idx)          │
                             │ updated_at                │
                             └────────┬──────────────────┘
                                      │ FK
                             ┌────────▼──────────────────┐
                             │     shortener_click        │
                             ├───────────────────────────┤
                             │ id (PK)                   │
                             │ url FK → shortener_url    │
                             │ clicked_at (idx)          │
                             │ ip_address                │
                             │ user_agent                │
                             │ country                   │
                             │ city                      │
                             │ referrer                  │
                             └───────────────────────────┘
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

Edit `.env`:

| Variable        | Description                                          | Example               |
| --------------- | ---------------------------------------------------- | --------------------- |
| `SECRET_KEY`    | Django secret key                                    | `django-insecure-...` |
| `DEBUG`         | Debug mode                                           | `True`                |
| `ALLOWED_HOSTS` | Comma-separated hosts                                | `localhost,127.0.0.1` |
| `DB_NAME`       | PostgreSQL database name                             | `urlshortener`        |
| `DB_USER`       | PostgreSQL user                                      | `postgres`            |
| `DB_PASSWORD`   | PostgreSQL password                                  | `admin321`            |
| `DB_HOST`       | `db` inside Docker Compose · `localhost` locally     | `localhost`           |
| `DB_PORT`       | `5432` inside Docker · `5435` locally (host-mapped)  | `5435`                |
| `LOG_LEVEL`     | `DEBUG` / `INFO` / `WARNING`                         | `INFO`                |

### 3. Run with Docker (recommended)

```bash
docker compose up --build
# App live at http://localhost:8000
# Migrations + tag seeding run automatically on startup
```

### 4. Run locally (without Docker)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py runserver
```

### 5. Install pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

Hooks: **ruff** (lint + import order) · **black** (formatting) · **mypy** (strict type checking)

---

## API Endpoints

### Core

| Method | Endpoint           | Description                              | Status |
| ------ | ------------------ | ---------------------------------------- | ------ |
| `POST` | `/api/v1/urls/`    | Shorten a URL (accepts tags + alias)     | 201    |
| `GET`  | `/<short_code>/`   | Redirect to original URL                 | 302    |
| `GET`  | `/health/`         | DB connectivity health check             | 200    |
| `GET`  | `/api/docs/`       | Swagger UI                               | 200    |
| `GET`  | `/api/schema/`     | Raw OpenAPI schema (JSON/YAML)           | 200    |

### Analytics (Mod 6)

| Method | Endpoint                          | Description                                    | Status |
| ------ | --------------------------------- | ---------------------------------------------- | ------ |
| `GET`  | `/api/v1/analytics/<short_code>/` | Click stats — total, by country, recent clicks | 200    |

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
  "custom_alias": null,
  "tags": [],
  "click_count": 0,
  "is_active": true,
  "is_expired": false,
  "expires_at": null,
  "title": null,
  "description": null,
  "favicon": null,
  "created_at": "2025-01-01T12:00:00Z"
}
```

### Shorten with tags and expiry (Mod 6)

```bash
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.example.com/campaign",
    "tags": ["Marketing", "Social"],
    "expires_at": "2025-12-31T23:59:59Z"
  }'
```

### Follow a redirect

```bash
curl -L http://localhost:8000/aB3xYz/
# → HTTP 302 → https://www.example.com/very/long/path
# Side effects: Click record logged, click_count incremented atomically
```

### View analytics (Mod 6)

```bash
curl http://localhost:8000/api/v1/analytics/aB3xYz/
```

Response `200 OK`:

```json
{
  "short_code": "aB3xYz",
  "original_url": "https://www.example.com/very/long/path",
  "click_count": 3,
  "is_active": true,
  "expires_at": null,
  "created_at": "2025-01-01T12:00:00Z",
  "clicks_by_country": [
    {"country": "RW", "total": 2},
    {"country": "US", "total": 1}
  ],
  "recent_clicks": [
    {
      "id": 3,
      "clicked_at": "2025-01-01T12:02:00Z",
      "ip_address": "1.2.3.4",
      "country": "US",
      "city": null,
      "user_agent": "Mozilla/5.0",
      "referrer": "https://google.com"
    }
  ]
}
```

### Health check

```bash
curl http://localhost:8000/health/
# {"status": "ok", "db": "reachable"}
```

---

## Running Tests

```bash
# Full suite (123 tests)
pytest

# With coverage report
coverage run -m pytest
coverage report --show-missing

# Enforce threshold (same as CI)
coverage report --fail-under=80

# HTML report
coverage html
start htmlcov/index.html      # Windows
open htmlcov/index.html       # macOS
```

Test breakdown:

| File                  | Tests | Covers                                                          |
| --------------------- | ----- | --------------------------------------------------------------- |
| `test_health.py`      | 5     | `GET /health/` — 200, fields, DB error propagation             |
| `test_models.py`      | 39    | User, Tag, URL, Click, URLManager, N+1 queries, aggregation     |
| `test_serializers.py` | 21    | All serializers — validation, creation, tags, analytics output  |
| `test_views.py`       | 31    | All views — create, redirect, click logging, analytics, 404s    |
| **Total**             | **123** |                                                               |

---

## Logging

Logs are written to both stdout and `logs/app.log` (rotated daily, 7-day retention).

```
2025-01-01 12:00:00 [INFO] shortener.views: POST /api/v1/urls/ — created short_code='aB3xYz' original_url='https://...'
2025-01-01 12:00:01 [INFO] shortener.views: GET /aB3xYz/ — redirecting to 'https://...' (click_count=1)
```

Control via `.env`:

```
LOG_LEVEL=DEBUG    # includes short_code generation + click_count increments
LOG_LEVEL=INFO     # default — API requests only
LOG_LEVEL=WARNING  # quiet — errors only
```

---

## Type Checking

```bash
mypy config/ shortener/ api/ core/ users/
```

Configured in `pyproject.toml` with `strict = true`, `django-stubs==6.0.3`, and `djangorestframework-stubs`.

---

## Module 5 Checklist — Foundation & Containerization

- [x] Modular Django project structure (`config`, `shortener`, `api`, `core` apps)
- [x] `python-decouple` for environment-based configuration with runtime validation
- [x] `URL` model with `original_url` (max 2048 chars) + `short_code` (unique, indexed)
- [x] Cryptographically secure short code generator (`secrets` module)
- [x] `POST /api/v1/urls/` — create short link with DRF serializer validation
- [x] `GET /<short_code>/` — HTTP 302 redirect
- [x] `GET /health/` — DB connectivity health check
- [x] Full type annotations on all views, serializers, and models (`mypy strict`)
- [x] Structured logging to stdout + rotating file (`logs/app.log`)
- [x] Full pytest suite — models, serializers, views, health check
- [x] Multi-stage Alpine `Dockerfile` with non-root user + `HEALTHCHECK`
- [x] `.dockerignore` to minimise build context and exclude secrets
- [x] `docker-compose.yml` — Django + PostgreSQL 15 with health check dependency
- [x] `drf-spectacular` Swagger/OpenAPI docs at `/api/docs/`
- [x] API versioning at `/api/v1/`
- [x] Pre-commit hooks: ruff + black + mypy
- [x] CI pipeline: lint → type-check → docker-build → django-check → pytest/coverage

---

## Module 6 Checklist — ORM & Data Access Layer

- [x] **Custom User model** — `User(AbstractUser)` with `is_premium` + `tier` (Free/Premium/Admin)
- [x] **`AUTH_USER_MODEL = "users.User"`** set before any migrations
- [x] **URL model expanded** — `owner` (FK), `click_count`, `is_active`, `expires_at`, `custom_alias`, `title`, `description`, `favicon`
- [x] **`URL.is_expired` property** — compares `expires_at` to `timezone.now()`
- [x] **`URL.increment_click_count()`** — atomic `F("click_count") + 1` update, no read-modify-write race
- [x] **`Tag` model** — `name` (unique), M2M with `URL`, alphabetically ordered
- [x] **`Click` model** — per-visit analytics: `ip_address`, `user_agent`, `country`, `city`, `referrer`, `clicked_at`
- [x] **`URLQuerySet`** — chainable: `active_urls()`, `expired_urls()`, `popular_urls(top_n)`
- [x] **`URLManager`** — exposes `URLQuerySet` methods directly on `URL.objects`
- [x] **Migration `0002_mod6_schema`** — all schema changes in one reviewable migration
- [x] **Migration `0003_seed_default_tags`** — data migration seeding 10 default tags, reversible, idempotent
- [x] **`select_related("owner")`** in `RedirectView` — fetches URL + owner in one SQL JOIN (N+1 prevention)
- [x] **`prefetch_related("clicks")`** in `URLAnalyticsView` — loads all clicks in one extra query (N+1 prevention)
- [x] **`annotate(Count)`** in `URLAnalyticsSerializer` — clicks-by-country computed in the DB, not Python
- [x] **Composite DB indexes** — `url_created_at_idx`, `url_active_expires_idx`, `click_url_country_idx`, `click_url_time_idx`
- [x] **`RedirectView` respects `is_active` and `is_expired`** — returns 404 for inactive/expired links
- [x] **`RedirectView` logs `Click`** — records ip, user_agent, referrer on every redirect
- [x] **`URLAnalyticsView`** — `GET /api/v1/analytics/<short_code>/`
- [x] **`URLCreateSerializer`** — accepts `tags` by name via `SlugRelatedField`
- [x] **`URLResponseSerializer`** — exposes all new fields including `tags` and `is_expired`
- [x] **`URLAnalyticsSerializer`** — aggregated stats with `clicks_by_country` + `recent_clicks`
- [x] **123 tests passing** — full coverage of all Mod 6 models, serializers, views, and query patterns
- [x] **CI workflow** — 5-job pipeline with coverage threshold enforcement and artifact uploads

---

## Engineering Patterns

### Abstract Base Classes (ABC)

`BaseShortCodeGenerator` enforces the generator interface. `@abstractmethod` prevents direct instantiation. `SecureShortCodeGenerator` is the production implementation using `secrets.choice` (cryptographically secure, unlike `random`).

```python
class BaseShortCodeGenerator(ABC):
    @abstractmethod
    def generate(self, length: int = 6) -> str: ...

    def __call__(self, length: int = 6) -> str:
        return self.generate(length)

class SecureShortCodeGenerator(BaseShortCodeGenerator):
    def generate(self, length: int = 6) -> str:
        return "".join(secrets.choice(self._alphabet) for _ in range(length))
```

### Protocols — Structural Subtyping (PEP 544)

`ShortCodeGenerator` is a `@runtime_checkable` Protocol. Any callable with the right signature satisfies it — no inheritance required. This is how `URLCreateSerializer` accepts a generator via DI without coupling to the ABC hierarchy.

```python
@runtime_checkable
class ShortCodeGenerator(Protocol):
    def __call__(self, length: int = 6) -> str: ...

def my_gen(length: int = 6) -> str:
    return "x" * length

assert isinstance(my_gen, ShortCodeGenerator)  # True — duck typing
```

### Custom QuerySet & Manager (Mod 6)

`URLQuerySet` provides chainable, reusable query methods. `URLManager` exposes them directly on `URL.objects` so call sites read like plain English.

```python
class URLQuerySet(models.QuerySet["URL"]):
    def active_urls(self) -> "URLQuerySet":
        return self.filter(is_active=True).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

    def popular_urls(self, top_n: int = 10) -> "URLQuerySet":
        return self.order_by("-click_count")[:top_n]

# Usage
URL.objects.active_urls().popular_urls(top_n=5)
```

### Atomic Counter Update — F() Expression (Mod 6)

`click_count` is incremented with `F()` to avoid the read-modify-write race condition that would occur under concurrent requests.

```python
def increment_click_count(self) -> None:
    # Translates to: UPDATE shortener_url SET click_count = click_count + 1
    # Safe under concurrent requests — no Python-level read involved.
    URL.objects.filter(pk=self.pk).update(click_count=F("click_count") + 1)
    self.refresh_from_db(fields=["click_count"])
```

### N+1 Query Prevention (Mod 6)

```python
# RedirectView — fetches URL + owner in ONE SQL JOIN
url = get_object_or_404(
    URL.objects.select_related("owner"),
    short_code=short_code,
)

# URLAnalyticsView — loads all clicks in ONE extra query
url = get_object_or_404(
    URL.objects.prefetch_related("clicks"),
    short_code=short_code,
)
```

### DB Aggregation with annotate() (Mod 6)

Clicks-by-country is computed entirely in PostgreSQL — never loaded into Python memory.

```python
def get_clicks_by_country(self, obj: URL) -> list[dict]:
    return list(
        obj.clicks
        .values("country")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
# SQL: SELECT country, COUNT(id) AS total FROM shortener_click
#      WHERE url_id = %s GROUP BY country ORDER BY total DESC
```

### Dependency Injection via Protocol

`URLCreateSerializer` accepts any `ShortCodeGenerator`-compatible callable at construction time. Tests inject a mock without subclassing anything.

```python
class URLCreateSerializer(serializers.ModelSerializer[URL]):
    def __init__(self, *args, generator: ShortCodeGenerator = default_generator, **kwargs):
        super().__init__(*args, **kwargs)
        self._generator = generator

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        short_code = self._generator(length=6)
        url = URL.objects.create(short_code=short_code, **validated_data)
        if tags:
            url.tags.set(tags)
        return url
```

### Data Migration — Seeding Default Tags (Mod 6)

```python
DEFAULT_TAGS = ["Marketing", "Social", "News", "Technology", "Education",
                "Entertainment", "Finance", "Health", "Travel", "Other"]

def seed_tags(apps, schema_editor):
    Tag = apps.get_model("shortener", "Tag")
    for name in DEFAULT_TAGS:
        Tag.objects.get_or_create(name=name)  # idempotent — safe to re-run

def unseed_tags(apps, schema_editor):
    Tag = apps.get_model("shortener", "Tag")
    Tag.objects.filter(name__in=DEFAULT_TAGS).delete()  # reversible
```

### Regex Validators

All patterns compiled once at module level — never inside functions.

```python
_SHORT_CODE_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9]{4,10}$")
_URL_SCHEME_PATTERN: re.Pattern[str] = re.compile(
    r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE
)
```

### Dataclasses & TypedDicts

Typed value objects decouple service logic from DRF serializer internals.

```python
@dataclass
class ShortenRequest:
    original_url: str

@dataclass
class ClickResult:
    url_id: int
    ip_address: str
    user_agent: str
    country: str | None = None
    city: str | None = None
    referrer: str | None = None

class HealthResponseDict(TypedDict):
    status: str
    db: str
```

---

_Python 3.11+ · Django 5.0 · DRF · PostgreSQL 15 · AmaliTech Training Program_
