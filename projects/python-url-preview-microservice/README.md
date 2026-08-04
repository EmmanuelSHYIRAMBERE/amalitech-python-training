# URL Preview Microservice

A standalone Django microservice with a **single responsibility**: fetch the title, description, and favicon of any URL on demand.

Designed to replace the in-process `url_preview` module in the URL Shortener service with a proper microservice that:
- Communicates over HTTP (not direct function calls)
- Authenticates callers via API keys
- Can be scaled and deployed independently
- Fails gracefully — the shortener keeps working if this service is down

---

## Architecture

```
┌──────────────────────────────────────┐
│  URL Shortener Service               │
│  (python-url-shortener-microservice) │
│                                      │
│  PREVIEW_SERVICE_URL=http://...      │
│  PREVIEW_SERVICE_TOKEN=<api-key>     │
│                                      │
│  shortener/preview_client.py  ──────────────────────────────────────┐
└──────────────────────────────────────┘                              │
                                                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  URL Preview Microservice  (this project)                                │
│                                                                          │
│  POST /api/v1/preview/fetch/   ← Authorization: Bearer <api-key>        │
│                                                                          │
│  preview/service.py                                                      │
│    ├── circuit breaker (Redis, per-domain, threshold=5, TTL=300s)       │
│    ├── retry (tenacity, exponential backoff 1s→2s→4s→8s, 3 attempts)   │
│    └── HTML parsing (regex, stdlib only)                                │
│                                                                          │
│  api_keys/                                                               │
│    ├── APIKey model (hashed tokens, request counting)                   │
│    └── APIKeyAuthentication backend                                      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start (Docker)

```bash
# 1. Clone and configure
cp .env.example .env
# Edit SECRET_KEY and DB_PASSWORD in .env

# 2. Start the service
docker compose up --build -d

# 3. Create an API key
curl -X POST http://localhost:8001/api/v1/keys/ \
  -H "Content-Type: application/json" \
  -d '{"name": "url-shortener"}'
# Response: {"id":1,"name":"url-shortener","token":"<64-char-hex>","created_at":"..."}

# 4. Copy the token — it is shown only once!
# Add to url-shortener's .env:
# PREVIEW_SERVICE_URL=http://localhost:8001
# PREVIEW_SERVICE_TOKEN=<token-from-step-3>

# 5. Test the endpoint
curl -X POST http://localhost:8001/api/v1/preview/fetch/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/health/` | None | Liveness check — DB + Redis status |
| `GET`  | `/api/docs/` | None | Swagger UI |
| `POST` | `/api/v1/keys/` | None* | Create a new API key |
| `GET`  | `/api/v1/keys/` | None* | List all API keys |
| `DELETE` | `/api/v1/keys/<id>/revoke/` | None* | Revoke an API key |
| `POST` | `/api/v1/preview/fetch/` | API Key | Fetch URL preview metadata |
| `GET`  | `/api/v1/preview/health/` | None | Preview service liveness |

> *Key management endpoints are open by design for bootstrapping. In production, restrict them via firewall/internal network.

### POST `/api/v1/preview/fetch/`

Request:
```json
{ "url": "https://example.com" }
```

Response (always 200 — errors reported in `error` field):
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "description": "This domain is for use in illustrative examples.",
  "favicon": "https://example.com/favicon.ico",
  "error": null
}
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | required | Django secret key |
| `DEBUG` | `False` | Debug mode |
| `ALLOWED_HOSTS` | `localhost` | Comma-separated allowed hosts |
| `DB_NAME` | `urlpreview` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | required | PostgreSQL password |
| `DB_HOST` | `db` | PostgreSQL host (Docker: `db`) |
| `DB_PORT` | `5432` | PostgreSQL port |
| `REDIS_URL` | `redis://redis:6379/0` | Redis URL (circuit breaker + cache) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:8000,...` | Allowed caller origins |
| `API_KEY_RATE_LIMIT` | `1000` | Max requests per day per API key |

---

## Connecting to the URL Shortener

In `python-url-shortener-microservice/.env`, set:

```bash
PREVIEW_SERVICE_URL=http://localhost:8001   # or http://preview-service:8001 in Docker
PREVIEW_SERVICE_TOKEN=<token-from-create-key>
```

The shortener's `preview_client.py` already reads these variables and will automatically use this microservice instead of the in-process fallback.

---

## Resiliency

### Circuit Breaker (Redis-backed)
- Opens after **5 consecutive failures** per domain
- Resets automatically after **300 seconds**
- While open: requests are rejected immediately (returns `error` field, no HTTP call)

### Retry (tenacity)
- Retries on `httpx.TimeoutException` and `httpx.NetworkError`
- **3 attempts** with exponential backoff: 1s → 2s → 4s → 8s max
- Does **not** retry on 4xx/5xx (those count as domain failures)

### Graceful Degradation
- `/api/v1/preview/fetch/` always returns **200**
- Errors are reported in the `error` field of the response
- The calling service (url-shortener) continues working

---

## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# With coverage
coverage run -m pytest && coverage report
```

---

## Project Structure

```
python-url-preview-microservice/
├── config/           # Settings, URLs, WSGI
├── core/             # HealthCheckView, TimeStampedModel
├── api_keys/         # APIKey model, authentication backend, management views
│   └── migrations/
├── preview/          # Service layer, views, serializers, circuit breaker
│   └── migrations/
├── api/              # URL aggregator (/api/v1/)
├── tests/            # Full TDD test suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Design Patterns Used

| Pattern | Where |
|---------|-------|
| **Single Responsibility** | Entire service — only URL preview, nothing else |
| **Microservice** | Deployed independently, communicates over HTTP |
| **API Key Auth** | `api_keys/authentication.py` — hashed tokens, no user accounts |
| **Circuit Breaker** | `preview/service.py` — Redis-backed, per-domain |
| **Retry + Backoff** | `preview/service.py` — tenacity, exponential |
| **Graceful Degradation** | Always returns 200 with `error` field |
| **ABC + Polymorphism** | `AbstractFetcher` → `DefaultFetcher` |
| **Frozen Dataclass** | `PreviewResult` — immutable value object |
| **NamedTuple** | `DomainInfo` — lightweight structured data |
| **Collections** | `FetchStats` — Counter, defaultdict, deque, OrderedDict |
| **Regex** | `preview/service.py` — HTML parsing without dependencies |
