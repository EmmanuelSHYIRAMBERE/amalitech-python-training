"""FastAPI route handlers for all LibraryMind endpoints."""

from fastapi import APIRouter, HTTPException

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
from app.dependencies import (
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


@router.post("/search/books", response_model=SearchBooksResponse)
def search_books(req: SearchBooksRequest):
    """Semantic vector search over the book catalogue."""
    try:
        vector = embedding_service.embed(req.query)
        results = vector_store.search(vector, req.limit)
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
        raise HTTPException(
            status_code=503, detail=f"Search failed: {e}"
        ) from e


@router.post("/search/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """RAG-grounded natural language question answering."""
    try:
        result = rag_engine.answer(req.question)
        return AskResponse(
            answer=result["answer"],
            sources=[
                BookResult(**{k: v for k, v in s.items()
                              if k in {"title", "author", "genre", "similarity"}})
                for s in result["sources"]
            ],
            cached=result["cached"],
        )
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI provider unavailable: {e}",
        ) from e


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Multi-turn conversational chat with per-session memory."""
    try:
        result = chatbot_service.chat(
            req.conversation_id, req.message
        )
        return ChatResponse(
            reply=result["reply"],
            sources=[
                BookResult(**{k: v for k, v in s.items()
                              if k in {"title", "author", "genre", "similarity"}})
                for s in result["sources"]
            ],
            conversation_id=result["conversation_id"],
        )
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI provider unavailable: {e}",
        ) from e


@router.post("/classify/ticket")
def classify_ticket(req: ClassifyTicketRequest):
    """Classify a support ticket into structured JSON."""
    try:
        return classification_service.classify(req.ticket_text)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except ClassificationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/summarise/reviews")
def summarise_reviews(req: SummariseRequest):
    """Summarise a batch of book reviews into structured JSON."""
    try:
        return summarisation_service.summarise(req.reviews)
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
