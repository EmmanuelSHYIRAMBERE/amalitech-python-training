import logging

from app.config import settings
from app.providers.amali_provider import AmaliProvider
from app.providers.resilient import ResilientAIService

logger = logging.getLogger(__name__)

# Model map — which model to use per provider name
_MODEL_MAP = {
    "openai":    settings.OPENAI_MODEL,
    "anthropic": settings.ANTHROPIC_MODEL,
}


def _build_providers() -> list:
    providers = []

    # Primary provider
    primary_model = _MODEL_MAP.get(
        settings.PRIMARY_PROVIDER, settings.OPENAI_MODEL
    )
    providers.append(AmaliProvider(
        api_key=settings.AMALI_API_KEY,
        base_url=settings.AMALI_BASE_URL,
        provider_name=settings.PRIMARY_PROVIDER,
        model=primary_model,
    ))

    # Fallback provider (only if different from primary)
    if (settings.FALLBACK_PROVIDER and
            settings.FALLBACK_PROVIDER != settings.PRIMARY_PROVIDER):
        fallback_model = _MODEL_MAP.get(
            settings.FALLBACK_PROVIDER, settings.ANTHROPIC_MODEL
        )
        providers.append(AmaliProvider(
            api_key=settings.AMALI_API_KEY,
            base_url=settings.AMALI_BASE_URL,
            provider_name=settings.FALLBACK_PROVIDER,
            model=fallback_model,
        ))

    logger.info(
        f"AI providers loaded: {[p.name for p in providers]} "
        f"(primary: {providers[0].name})"
    )
    return providers


ai_service = ResilientAIService(_build_providers())
