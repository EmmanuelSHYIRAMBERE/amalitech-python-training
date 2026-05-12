# AI FastAPI Capstone — Prompt Engineering

A capstone project for Applied AI & Prompt Engineering that demonstrates a
**multi-stage AI workflow** for automating backend API development — from natural
language spec through structured JSON to production-ready FastAPI code.

---

## Overview

This project explores how two AI tools can be chained together in a structured
pipeline to produce working backend code with minimal manual intervention:

1. **Claude** (chat AI) converts a natural-language description into a precise,
   machine-readable JSON resource specification.
2. **GitHub Copilot** (IDE AI) reads that JSON spec and generates FastAPI
   boilerplate — Pydantic schemas, route handlers, business logic, and an
   in-memory store.
3. The output is refactored into a clean multi-file architecture following
   production-style layering principles.

The result is a fully functional `Order` REST API for an e-commerce backend,
built almost entirely through prompt engineering.

---

## Problem Statement

Writing boilerplate for CRUD APIs is repetitive and error-prone. Developers
spend significant time translating business requirements into schemas, validation
rules, and endpoint definitions. This project asks: **can two AI tools, chained
through a structured data contract, automate that translation end-to-end?**

---

## AI Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Stage 1 — Specification Generation                             │
│                                                                 │
│  Human prompt  ──►  Claude (claude.ai)  ──►  order_resource.json│
│  "Design an Order                          (fields, validation, │
│   resource for an                           endpoints, enums)   │
│   e-commerce API"                                               │
└──────────────────────────────┬──────────────────────────────────┘
                               │ JSON spec passed as context
┌──────────────────────────────▼──────────────────────────────────┐
│  Stage 2 — Code Generation                                      │
│                                                                 │
│  order_resource.json  ──►  GitHub Copilot  ──►  main.py         │
│                            (VS Code IDE AI)    (monolithic       │
│                                                 boilerplate)    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ generated code refactored
┌──────────────────────────────▼──────────────────────────────────┐
│  Stage 3 — Architecture Refactor                                │
│                                                                 │
│  main.py (flat)  ──►  Claude (Claude Code)  ──►  5-module layout│
│                        "split into clean                        │
│                         production layers"                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
ai-fastapi-capstone-prompt-engineering/
├── order_resource.json   ← Stage 1 output — shared API spec (source of truth)
├── models.py             ← Pydantic schemas + OrderStatus enum
├── database.py           ← In-memory store (_db dict + _next_id counter)
├── services.py           ← Business logic, CRUD functions, transition guards
├── routes.py             ← FastAPI route handlers (thin delegation layer)
├── main.py               ← App initialisation + router registration
├── pr.md                 ← Pull request description
└── README.md             ← This file
```

### Layer responsibilities

| File | Imports from | Responsibility |
|------|-------------|----------------|
| `models.py` | `pydantic` only | Data contracts — no framework logic |
| `database.py` | `models` | State — the only place raw data lives |
| `services.py` | `models`, `database`, `fastapi` | Rules — transition guards, subtotals, CRUD |
| `routes.py` | `models`, `services`, `fastapi` | HTTP — parsing, delegation, response codes |
| `main.py` | `fastapi`, `routes` | Wiring — app creation and router inclusion |

---

## Tech Stack

| Tool | Role |
|------|------|
| Python 3.11+ | Runtime |
| FastAPI | Web framework + automatic OpenAPI docs |
| Pydantic v2 | Schema definition and request validation |
| Uvicorn | ASGI server |
| Claude AI | Spec generation + architecture refactoring |
| GitHub Copilot | Boilerplate code generation from JSON spec |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training.git
cd amalitech-python-training/projects/ai-fastapi-capstone-prompt-engineering

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# Install dependencies
pip install fastapi pydantic uvicorn
```

---

## Running Locally

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive documentation (Swagger UI): `http://localhost:8000/docs`
Alternative docs (ReDoc): `http://localhost:8000/redoc`

---

## API Endpoints

| Method | Path | Status codes | Description |
|--------|------|-------------|-------------|
| `POST` | `/orders` | 201, 422 | Create a new order |
| `GET` | `/orders` | 200 | List orders (paginated, filterable) |
| `GET` | `/orders/{order_id}` | 200, 404 | Retrieve a single order |
| `PATCH` | `/orders/{order_id}` | 200, 404, 409 | Update order status or details |
| `DELETE` | `/orders/{order_id}` | 204, 404, 409 | Delete an order |

### Query parameters for `GET /orders`

| Parameter | Type | Default | Constraint |
|-----------|------|---------|-----------|
| `skip` | integer | 0 | `≥ 0` |
| `limit` | integer | 20 | `1 – 100` |
| `status` | enum | — | `pending / confirmed / shipped / delivered / cancelled` |
| `customer_id` | integer | — | `> 0` |

### Status transition rules

```
pending   →  confirmed, cancelled
confirmed →  shipped,   cancelled
shipped   →  delivered
delivered →  (terminal)
cancelled →  (terminal)
```

Orders with status `shipped` or `delivered` cannot be deleted.

---

## Demo Workflow

### 1. Create an order

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "items": [{"product_id": 10, "quantity": 2, "unit_price": 9.99}],
    "shipping_address": "123 Main Street, Springfield"
  }'
```

```json
{
  "id": 1,
  "customer_id": 1,
  "status": "pending",
  "items": [{"product_id": 10, "quantity": 2, "unit_price": 9.99, "subtotal": 19.98}],
  "total_price": 19.98,
  "shipping_address": "123 Main Street, Springfield",
  "notes": null,
  "created_at": "2026-05-12T10:00:00Z",
  "updated_at": "2026-05-12T10:00:00Z"
}
```

### 2. Advance the order status

```bash
curl -X PATCH http://localhost:8000/orders/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

### 3. Attempt an invalid transition

```bash
curl -X PATCH http://localhost:8000/orders/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "pending"}'
# HTTP 409 — Cannot transition from 'confirmed' to 'pending'
```

### 4. List filtered orders

```bash
curl "http://localhost:8000/orders?status=confirmed&limit=10"
```

---

## Learning Outcomes

- **Prompt engineering for structured output** — crafting prompts that produce
  machine-readable JSON rather than prose, making AI output composable with other
  tools.
- **AI chaining** — using the output of one AI (Claude → JSON spec) as the input
  context for another (Copilot → code), reducing ambiguity at each handoff.
- **Clean architecture in FastAPI** — separating schemas, state, business logic,
  and routing into explicit layers with one-directional dependencies.
- **Pydantic v2 validation** — field-level constraints (`gt`, `ge`, `le`,
  `min_length`, `max_length`) enforced declaratively from a spec.
- **Business rule encoding** — translating natural-language constraints
  ("only forward transitions", "address locked after pending") into code that
  raises the correct HTTP error codes.

---

## Future Improvements

- **Persistent storage** — replace the in-memory dict with a PostgreSQL backend
  via SQLAlchemy or SQLModel.
- **Authentication** — add JWT-based auth so only order owners can update or
  delete their orders.
- **Automated spec-to-code pipeline** — build a CLI tool that reads any
  `*_resource.json` and scaffolds the full module set automatically.
- **Test suite** — add pytest coverage for all service functions and route
  handlers, including transition guard edge cases.
- **Docker** — containerise the app with a `Dockerfile` and
  `docker-compose.yml` for one-command local setup.
- **Async handlers** — convert route functions to `async def` and swap the
  in-memory store for an async-compatible database driver.
