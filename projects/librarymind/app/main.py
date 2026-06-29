"""LibraryMind FastAPI application entry point.

Creates the FastAPI ``app`` instance, configures CORS, attaches the
router, and logs startup/shutdown events via a lifespan context manager.
"""

# warnings must be silenced before any third-party imports to suppress
# their startup noise (chromadb telemetry, openai deprecation notices).
import warnings

warnings.filterwarnings("ignore")

import logging  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.api.routes import router  # noqa: E402
from app.config import validate_and_summarise  # noqa: E402
from app.dependencies import vector_store  # noqa: E402
from app.providers import ai_service  # noqa: E402

# Silence noisy third-party libraries before basicConfig sets the root level
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Re-silence third party AFTER basicConfig (basicConfig resets root handler)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Log startup information and run shutdown housekeeping."""
    logger.info("LibraryMind API starting up")
    validate_and_summarise()
    logger.info(f"Vector store books: {vector_store.count()}")
    logger.info(f"AI provider: {ai_service.primary_provider_name}")
    yield
    logger.info("LibraryMind API shutting down")


app = FastAPI(
    title="LibraryMind API",
    description="AI-powered intelligent library assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
