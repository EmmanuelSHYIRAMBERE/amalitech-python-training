"""LibraryMind FastAPI application entry point.

Creates the FastAPI ``app`` instance, configures CORS, attaches the
router, and logs startup/shutdown events via a lifespan context manager.
"""

import warnings
warnings.filterwarnings("ignore")

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import validate_and_summarise
from app.dependencies import vector_store
from app.providers import ai_service

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
