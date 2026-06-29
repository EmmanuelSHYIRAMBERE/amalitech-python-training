import httpx
import openai

from app.config import settings
from app.infrastructure import cache, rate_limiter, usage_tracker
from app.providers import ai_service
from app.services.chatbot import ChatbotService
from app.services.classification import ClassificationService
from app.services.embedding import EmbeddingService
from app.services.rag_engine import RAGEngine
from app.services.summarisation import SummarisationService
from app.services.vector_store import VectorStore

# openai SDK pointed at Amalitec proxy with SSL verification disabled
_openai_client = openai.OpenAI(
    api_key=settings.AMALI_API_KEY,
    base_url=settings.AMALI_BASE_URL,
    http_client=httpx.Client(verify=False),
)

embedding_service = EmbeddingService(
    _openai_client, cache, settings.EMBEDDING_MODEL
)
vector_store = VectorStore(settings.CHROMA_DB_PATH)
rag_engine = RAGEngine(
    embedding_service=embedding_service,
    vector_store=vector_store,
    ai_service=ai_service,
    cache=cache,
    rate_limiter=rate_limiter,
    usage_tracker=usage_tracker,
    threshold=settings.RELEVANCE_THRESHOLD,
)
chatbot_service = ChatbotService(
    rag_engine, ai_service, settings.MAX_HISTORY_MESSAGES
)
classification_service = ClassificationService(ai_service, rate_limiter)
summarisation_service = SummarisationService(ai_service, rate_limiter)
