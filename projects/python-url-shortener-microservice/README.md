# URL Shortener Microservice — Module 5

> **Phase 1 Foundation** · Django 5.0+ · DRF · PostgreSQL 15 · Docker

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

## Project Structure

```
url-shortener-microservice/
├── config/
│   ├── settings.py       # python-decouple config
│   ├── urls.py           # root router + Swagger
│   └── wsgi.py
├── shortener/
│   ├── models.py         # URL model + short_code generator
│   ├── serializers.py    # DRF serializers with URL validation
│   ├── views.py          # POST create + GET redirect
│   ├── urls.py           # /<short_code>/ redirect route
│   └── migrations/
├── api/
│   └── urls.py           # /api/v1/ versioned routes
├── Dockerfile            # multi-stage build
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/urls/` | Shorten a URL → returns `short_code` + `short_url` |
| `GET` | `/<short_code>/` | Redirect to original URL (HTTP 302) |
| `GET` | `/api/docs/` | Swagger UI (drf-spectacular) |
| `GET` | `/api/schema/` | OpenAPI schema (JSON) |

## Running with Docker

```bash
# 1. Copy env file
cp .env.example .env

# 2. Build and start
docker compose up --build

# 3. Service is live at http://localhost:8000
```

## Running Locally (without Docker)

```bash
pip install -r requirements.txt

# Point DB_HOST=localhost in .env, then:
python manage.py migrate
python manage.py runserver
```

## Example Usage

```bash
# Shorten a URL
curl -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.example.com/very/long/path"}'

# Response
{
  "short_code": "aB3xYz",
  "original_url": "https://www.example.com/very/long/path",
  "short_url": "http://localhost:8000/aB3xYz/",
  "created_at": "2025-01-01T12:00:00Z"
}

# Redirect (browser or curl -L)
curl -L http://localhost:8000/aB3xYz/
```

## Module 5 Checklist

- [x] Modular Django project structure (`config`, `shortener`, `api` apps)
- [x] `python-decouple` for environment-based configuration
- [x] MVP `URL` model with `original_url` + `short_code` (indexed)
- [x] 6-character alphanumeric short code generator (collision-safe)
- [x] `POST /api/v1/urls/` — create short link with DRF serializer validation
- [x] `GET /<short_code>/` — HTTP 302 redirect
- [x] Multi-stage `Dockerfile` (lightweight Python image)
- [x] `docker-compose.yml` — Django + PostgreSQL 15 with health check
- [x] `drf-spectacular` Swagger/OpenAPI docs at `/api/docs/`
- [x] API versioning at `/api/v1/`

---

*Python 3.11+ · Django 5.0 · DRF · PostgreSQL 15 · AmaliTech Training Program*
