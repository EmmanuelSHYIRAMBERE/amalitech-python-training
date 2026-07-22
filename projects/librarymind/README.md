# LibraryMind

LibraryMind is an AI-powered library assistant backend built with FastAPI and Python.
It provides semantic book search, retrieval-augmented question answering, multi-turn
conversational chat, support ticket classification, and book review summarisation —
all routed through the Amalitec AI proxy.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI 0.115 |
| ASGI server | Uvicorn 0.30 |
| AI proxy client | httpx 0.27 + openai SDK 1.40 |
| Vector store | ChromaDB 0.5.5 (cosine similarity) |
| Embeddings | Local numpy bag-of-words (SHA-256 seeded, 1536-dim) |
| Config | pydantic-settings |
| Retry / resilience | Tenacity |
| Caching | Redis 5 (optional — gracefully disabled if not running) |
| AI providers | Amalitec proxy → OpenAI GPT-3.5-turbo / Anthropic claude-haiku-4-5 |

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd librarymind
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your Amalitec API key:

```
AMALI_API_KEY=your_actual_key_here
```

### 5. Seed the vector database

```bash
python scripts/seed.py
```

This embeds all 25 books from `data/books.json` into ChromaDB.
Run once — re-running is safe (upserts existing records).

### 6. Start the server

```bash
uvicorn app.main:app --port 8000
```

The API is now available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`.

---

## Environment Variables

All variables are read from `.env`. Copy `.env.example` to get started.

| Variable | Default | Description |
|---|---|---|
| `AMALI_API_KEY` | *(required)* | Amalitec proxy API key |
| `AMALI_BASE_URL` | `https://ai-api.amalitech.org/api/v2/public/` | Proxy base URL |
| `PRIMARY_PROVIDER` | `openai` | Primary AI provider (`openai` or `anthropic`) |
| `FALLBACK_PROVIDER` | `anthropic` | Fallback if primary fails |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | Model for OpenAI routing |
| `ANTHROPIC_MODEL` | `claude-haiku-4-5` | Model for Anthropic routing |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL (optional) |
| `RATE_LIMIT_PER_MINUTE` | `20` | Max AI calls per minute |
| `CACHE_TTL_SECONDS` | `3600` | Redis cache TTL in seconds |
| `RELEVANCE_THRESHOLD` | `0.05` | Minimum similarity score to include a result |
| `MAX_HISTORY_MESSAGES` | `10` | Max messages retained per chat session |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model name (kept for interface compatibility) |
| `CHROMA_DB_PATH` | `./chroma_db` | Path to ChromaDB persistence directory |

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `POST` | `/search/books` | Semantic vector search over the book catalogue |
| `POST` | `/search/ask` | RAG-grounded natural language question answering |
| `POST` | `/chat` | Multi-turn conversational chat with memory |
| `POST` | `/classify/ticket` | Classify a support ticket into structured JSON |
| `POST` | `/summarise/reviews` | Summarise a batch of book reviews into structured JSON |
| `GET` | `/health` | Server health check and daily cost report |

### Request / Response shapes

**`POST /search/books`**
```json
// Request
{ "query": "desert planet adventure", "limit": 5 }

// Response
{
  "results": [
    { "title": "Dune", "author": "Frank Herbert", "genre": "Science Fiction", "similarity": 0.312 }
  ],
  "total": 1
}
```

**`POST /search/ask`**
```json
// Request
{ "question": "What science fiction books do you have about space?" }

// Response
{
  "answer": "We have two science fiction books about space ...",
  "sources": [ { "title": "Dune", "author": "Frank Herbert", "genre": "Science Fiction", "similarity": 0.31 } ],
  "cached": false
}
```

**`POST /chat`**
```json
// Request
{ "conversation_id": "session-abc", "message": "Recommend a thriller" }

// Response
{
  "reply": "I recommend Gone Girl by Gillian Flynn ...",
  "sources": [ { "title": "Gone Girl", "author": "Gillian Flynn", "genre": "Crime Thriller", "similarity": 0.28 } ],
  "conversation_id": "session-abc"
}
```

**`POST /classify/ticket`**
```json
// Request
{ "ticket_text": "My library card is broken and I am very frustrated." }

// Response
{
  "category": "technical",
  "priority": "high",
  "sentiment": "negative",
  "department": "library card assistance",
  "summary": "Library card not working, causing patron frustration."
}
```

**`POST /summarise/reviews`**
```json
// Request
{ "reviews": ["Loved it!", "Pacing was slow.", "Brilliant ending."] }

// Response
{
  "overall_sentiment": "mixed",
  "average_rating": 3.8,
  "key_themes": ["pacing", "ending"],
  "praise": ["engaging ending"],
  "criticism": ["slow pacing"],
  "recommendation": "Worth reading for fans of the genre."
}
```

**`GET /health`**
```json
{ "status": "ok", "daily_cost_usd": 0.000412, "total_requests": 14 }
```

---

## Sample curl Commands

```bash
# Semantic book search
curl -s -X POST http://localhost:8000/search/books \
  -H "Content-Type: application/json" \
  -d '{"query": "desert planet adventure", "limit": 3}' | python -m json.tool

# RAG question answering
curl -s -X POST http://localhost:8000/search/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Recommend a classic romance novel set in England"}' | python -m json.tool

# Multi-turn chat (turn 1)
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "my-session", "message": "Recommend a thriller book"}' | python -m json.tool

# Multi-turn chat (turn 2 — same session)
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "my-session", "message": "Tell me more about that one"}' | python -m json.tool

# Classify a support ticket
curl -s -X POST http://localhost:8000/classify/ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_text": "The internet in the library is very slow and I cannot access the catalogue."}' | python -m json.tool

# Summarise book reviews
curl -s -X POST http://localhost:8000/summarise/reviews \
  -H "Content-Type: application/json" \
  -d '{"reviews": ["Loved it, great characters.", "Pacing was slow in the middle.", "Brilliant ending, highly recommend."]}' | python -m json.tool

# Health check
curl -s http://localhost:8000/health | python -m json.tool
```

---

## Code Quality

Pre-commit hooks are configured in `.pre-commit-config.yaml`.
To enable locally (requires internet access):

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Tools configured: Black (formatting), Ruff (linting),
pre-commit-hooks (trailing whitespace, merge conflict detection).

---

## Docker Deployment

```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your AMALI_API_KEY

# Start all services (API + Redis)
docker-compose up --build

# Seed the database (first time only)
docker-compose exec api python scripts/seed.py
```

Note: When running with Docker, Redis is fully enabled and
caching will be active. The ChromaDB data is persisted in
a named volume (`chroma_data`).

---

## Known Limitations

### Local bag-of-words embeddings
The Amalitec proxy `/embeddings` endpoint returns an empty `200 OK` (stub not yet
implemented). All external model downloads (ChromaDB ONNX, tiktoken vocabulary files)
are also blocked by the corporate SSL proxy. As a workaround, embeddings are computed
locally using a deterministic SHA-256 seeded numpy bag-of-words model (1536-dim,
L2-normalised). This produces consistent vectors with no network dependency, but
similarity scores are lower (0.05–0.31) than neural embeddings (typically 0.7+).

### RELEVANCE_THRESHOLD=0.05
Because bag-of-words similarity scores are in the 0.05–0.31 range rather than the
0.7+ range of neural embeddings, the relevance threshold is set to 0.05. This means
queries with any shared vocabulary with book descriptions will return results. When
the proxy `/embeddings` endpoint is available, raise the threshold to 0.25 or higher.

### Redis is optional
The application starts and runs correctly without Redis. Caching is gracefully
disabled when the Redis connection is refused. Run a local Redis instance and set
`REDIS_URL` to enable response caching and reduce API calls.

### Off-topic detection
Because the threshold is 0.05, natural-language off-topic queries (e.g. "What is
the weather today?") may still match books via shared common words. The smoke test
uses a nonsense string (`"xyzzy plugh blorb"`) to guarantee zero vocabulary overlap
and test the true no-match path.
