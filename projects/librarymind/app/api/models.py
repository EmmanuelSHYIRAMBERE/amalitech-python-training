from pydantic import BaseModel, Field

# ── Request models ──────────────────────────────────────


class SearchBooksRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)


class ChatRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)


class ClassifyTicketRequest(BaseModel):
    ticket_text: str = Field(..., min_length=10, max_length=5000)


class SummariseRequest(BaseModel):
    reviews: list[str] = Field(..., min_length=1, max_length=50)


# ── Response models ─────────────────────────────────────


class BookResult(BaseModel):
    title: str
    author: str
    genre: str
    similarity: float


class SearchBooksResponse(BaseModel):
    results: list[BookResult]
    total: int


class AskResponse(BaseModel):
    answer: str
    sources: list[BookResult]
    cached: bool


class ChatResponse(BaseModel):
    reply: str
    sources: list[BookResult]
    conversation_id: str


class HealthResponse(BaseModel):
    status: str
    daily_cost_usd: float
    total_requests: int
