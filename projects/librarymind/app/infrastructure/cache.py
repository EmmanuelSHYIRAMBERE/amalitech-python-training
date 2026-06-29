"""Redis-backed cache service with graceful degradation."""

import hashlib
import json
import logging
from typing import Any, Optional

import redis

logger = logging.getLogger(__name__)


class CacheService:
    """JSON cache backed by Redis, with transparent no-op fallback.

    If Redis is unavailable at construction time (or at any point
    during operation), all methods silently return ``None`` / no-op
    so the application continues without caching.

    Args:
        redis_url: Redis connection string (e.g. ``redis://localhost:6379``).
        default_ttl: Default key expiry in seconds (default: 3600).

    Attributes:
        available: ``True`` when Redis is connected and healthy.

    Example:
        >>> cache = CacheService("redis://localhost:6379")
        >>> cache.set("my-key", {"data": 42})
        >>> cache.get("my-key")
        {'data': 42}
    """

    def __init__(self, redis_url: str, default_ttl: int = 3600) -> None:
        self.default_ttl = default_ttl
        try:
            self.client = redis.from_url(redis_url)
            self.client.ping()
            self.available = True
            logger.info("Redis cache connected")
        except Exception as e:
            self.available = False
            logger.warning(f"Redis unavailable — running without cache: {e}")

    def _make_key(self, raw: str) -> str:
        """Hash a raw string to a fixed-length Redis key.

        Args:
            raw: The raw cache key (e.g. a question string).

        Returns:
            64-character hex SHA-256 digest of the input.
        """
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, raw_key: str) -> Optional[Any]:
        """Retrieve a cached value by its raw key.

        Args:
            raw_key: The original (unhashed) key string.

        Returns:
            The deserialised value, or ``None`` on a miss or error.
        """
        if not self.available:
            return None
        try:
            value = self.client.get(self._make_key(raw_key))
            if value:
                logger.debug("Cache HIT")
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    def set(self, raw_key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in Redis under the hashed key.

        Args:
            raw_key: The original (unhashed) key string.
            value: JSON-serialisable value to store.
            ttl: Override expiry in seconds; defaults to ``default_ttl``.
        """
        if not self.available:
            return
        try:
            self.client.setex(
                self._make_key(raw_key),
                ttl or self.default_ttl,
                json.dumps(value),
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")

    def delete(self, raw_key: str) -> None:
        """Delete a key from Redis.

        Args:
            raw_key: The original (unhashed) key string to remove.
        """
        if not self.available:
            return
        try:
            self.client.delete(self._make_key(raw_key))
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
