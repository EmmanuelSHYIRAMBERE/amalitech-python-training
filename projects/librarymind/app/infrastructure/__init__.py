from app.config import settings
from app.infrastructure.cache import CacheService
from app.infrastructure.rate_limiter import RateLimiter
from app.infrastructure.usage_tracker import UsageTracker

cache = CacheService(settings.REDIS_URL, settings.CACHE_TTL_SECONDS)
rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)
usage_tracker = UsageTracker()
