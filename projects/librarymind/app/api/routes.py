"""FastAPI route handlers for all LibraryMind endpoints.

Authentication is optional on all AI endpoints.  Unauthenticated callers
receive a restricted experience; authenticated callers get full access.

  /search/books  — unauthenticated: limit capped at PUBLIC_SEARCH_LIMIT
  /search/ask    — unauthenticated: answer only, sources list is empty
  /chat          — unauthenticated: single-turn only (history not saved)
  /classify/ticket — unauthenticated: category field only
  /summarise/reviews — unauthenticated: recommendation field only
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.models import (
    AskRequest,
    AskResponse,
    BookResult,
    ChatRequest,
    ChatResponse,
    ClassifyTicketRequest,
    HealthResponse,
    SearchBooksRequest,
    SearchBooksResponse,
    SummariseRequest,
)
from app.auth.dependencies import get_optional_user
from app.config import settings
from app.dependencies import (
    ai_service,
    chatbot_service,
    classification_service,
    embedding_service,
    rag_engine,
    summarisation_service,
    usage_tracker,
    vector_store,
)
from app.exceptions import (
    ClassificationError,
    RateLimitError,
    SummarisationError,
)

router = APIRouter()


logger = logging.getLogger(__name__)


@router.post("/search/books", response_model=SearchBooksResponse)
def search_books(
    req: SearchBooksRequest,
    current_user: dict | None = Depends(get_optional_user),  # noqa: B008
):
    """Semantic vector search over the book catalogue.

    Unauthenticated: results capped at PUBLIC_SEARCH_LIMIT.
    Authenticated: full requested limit (up to 20).

    The query is analysed by the AI to extract hard filters (author name,
    author gender, genre) and clean search keywords before embedding, so
    both structural queries ("by Emily", "by a female") and thematic
    queries ("gripping thriller") return relevant results.
    """
    try:
        effective_limit = (
            req.limit if current_user else min(req.limit, settings.PUBLIC_SEARCH_LIMIT)
        )
        # Reuse the RAG engine's filter extraction — same logic, same cache
        where_filter, search_keywords = rag_engine._extract_filters(req.query)  # noqa: SLF001
        logger.info(
            f"search_books — keywords={search_keywords!r}, filter={where_filter}"
        )
        vector = embedding_service.embed(search_keywords)
        results = vector_store.search(vector, effective_limit, where=where_filter)
        books = [
            BookResult(
                title=r["title"],
                author=r["author"],
                genre=r["genre"],
                similarity=r["similarity"],
            )
            for r in results
        ]
        return SearchBooksResponse(results=books, total=len(books))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Search failed: {e}") from e


@router.post("/search/ask", response_model=AskResponse)
def ask(
    req: AskRequest,
    current_user: dict | None = Depends(get_optional_user),  # noqa: B008
):
    """RAG-grounded natural language question answering.

    Unauthenticated: answer only, sources list omitted.
    Authenticated: full answer with source citations.
    """
    try:
        result = rag_engine.answer(req.question)
        sources = (
            [
                BookResult(
                    **{
                        k: v
                        for k, v in s.items()
                        if k in {"title", "author", "genre", "similarity"}
                    }
                )
                for s in result["sources"]
            ]
            if current_user
            else []
        )
        return AskResponse(
            answer=result["answer"], sources=sources, cached=result["cached"]
        )
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(
            status_code=503, detail=f"AI provider unavailable: {e}"
        ) from e


@router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    current_user: dict | None = Depends(get_optional_user),  # noqa: B008
):
    """Multi-turn conversational chat with per-session memory.

    Unauthenticated: single-turn only — history is never saved.
    Authenticated: full multi-turn with persistent session history.
    """
    try:
        if current_user:
            result = chatbot_service.chat(req.conversation_id, req.message)
        else:
            # Single-turn: answer without touching the session store
            result = chatbot_service.chat("__anon__", req.message)
            chatbot_service.store.pop("__anon__", None)
            result["conversation_id"] = req.conversation_id

        return ChatResponse(
            reply=result["reply"],
            sources=[
                BookResult(
                    **{
                        k: v
                        for k, v in s.items()
                        if k in {"title", "author", "genre", "similarity"}
                    }
                )
                for s in result["sources"]
            ],
            conversation_id=result["conversation_id"],
        )
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(
            status_code=503, detail=f"AI provider unavailable: {e}"
        ) from e


@router.post("/classify/ticket")
def classify_ticket(
    req: ClassifyTicketRequest,
    current_user: dict | None = Depends(get_optional_user),  # noqa: B008
):
    """Classify a support ticket into structured JSON.

    Unauthenticated: category field only.
    Authenticated: full structured JSON (category, priority, suggested_team, summary).
    """
    try:
        full = classification_service.classify(req.ticket_text)
        if current_user:
            return full
        return {"category": full.get("category")}
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except ClassificationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/summarise/reviews")
def summarise_reviews(
    req: SummariseRequest,
    current_user: dict | None = Depends(get_optional_user),  # noqa: B008
):
    """Summarise a batch of book reviews into structured JSON.

    Unauthenticated: recommendation field only.
    Authenticated: full structured JSON (overall_sentiment, average_rating, key_themes, recommendation).
    """
    try:
        full = summarisation_service.summarise(req.reviews)
        if current_user:
            return full
        return {"recommendation": full.get("recommendation")}
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except (SummarisationError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/health", response_model=HealthResponse)
def health():
    """Return server health status and daily cost summary."""
    return HealthResponse(
        status="ok",
        daily_cost_usd=round(usage_tracker.get_daily_cost(), 6),
        total_requests=usage_tracker.total_requests(),
    )
