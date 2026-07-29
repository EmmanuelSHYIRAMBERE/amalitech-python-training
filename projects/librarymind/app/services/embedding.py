"""Text embedding service with proxy-backed neural embeddings.

Attempts to use the Amalitec proxy's ``/embeddings`` endpoint via the
OpenAI SDK (``text-embedding-3-small``, 1536-dim).  If the proxy returns
an empty or invalid response — which happens when the endpoint is a stub —
it falls back automatically to a local deterministic bag-of-words model
so the application stays functional.

The local fallback uses SHA-256-seeded numpy word vectors summed and
L2-normalised to 1536 dimensions.  It is order-independent and produces
lower similarity scores than neural embeddings (0.05–0.31 vs 0.7+), but
it is deterministic, requires no network calls, and matches the same
interface so it can be swapped out transparently.
"""

import hashlib
import logging
import struct
from typing import Any

import numpy as np

from app.infrastructure.cache import CacheService

logger = logging.getLogger(__name__)

_DIMS = 1536


# ---------------------------------------------------------------------------
# Local bag-of-words fallback
# ---------------------------------------------------------------------------

def _word_vector(word: str) -> np.ndarray:
    """Map a single word to a deterministic unit vector in _DIMS-space."""
    digest = hashlib.sha256(word.encode()).digest()
    seed = struct.unpack("<Q", digest[:8])[0]
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(_DIMS).astype(np.float32)
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


def _local_embed(text: str) -> list[float]:
    """Bag-of-words embedding: sum unit word vectors then L2-normalise."""
    words = text.lower().split()
    if not words:
        return [0.0] * _DIMS
    vec = np.zeros(_DIMS, dtype=np.float32)
    for w in words:
        vec += _word_vector(w)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec.tolist()


# ---------------------------------------------------------------------------
# Embedding service
# ---------------------------------------------------------------------------

class EmbeddingService:
    """Generates text embeddings, preferring the proxy neural model.

    On every call ``embed()`` first tries ``client.embeddings.create()``
    against the Amalitec proxy (``text-embedding-3-small``, 1536-dim).
    If the proxy returns a valid non-empty vector that call succeeds and
    the result is cached in Redis for 24 h.

    If the proxy endpoint is unavailable or returns an empty/stub response,
    the call falls back to the local deterministic bag-of-words model
    transparently.  A WARNING is logged on each fallback so the operator
    knows the proxy embedding is not in service.

    Args:
        openai_client: OpenAI SDK client pointed at the Amalitec proxy.
        cache: Redis-backed cache for computed embeddings.
        model: Embedding model name forwarded to the proxy.

    Example:
        >>> svc = EmbeddingService(client, cache, "text-embedding-3-small")
        >>> vec = svc.embed("Dune by Frank Herbert")
        >>> len(vec)
        1536
    """

    def __init__(
        self,
        openai_client: Any,
        cache: CacheService,
        model: str = "text-embedding-3-small",
    ) -> None:
        self.client = openai_client
        self.cache = cache
        self.model = model

    def embed(self, text: str) -> list[float]:
        """Return a 1536-dim embedding vector for *text*.

        Resolution order:
        1. Redis cache hit → return immediately
        2. Amalitec proxy ``/embeddings`` → neural embedding
        3. Local bag-of-words fallback (proxy unavailable or stub)

        Args:
            text: Text to embed (any length).

        Returns:
            List of 1536 floats, L2-normalised.
        """
        cache_key = f"emb:{self.model}:{text}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug("Embedding cache hit")
            return cached

        vector = self._proxy_embed(text)
        self.cache.set(cache_key, vector, ttl=86400)
        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts, each cached independently.

        Args:
            texts: Strings to embed.

        Returns:
            List of embedding vectors in the same order as *texts*.
        """
        return [self.embed(t) for t in texts]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _proxy_embed(self, text: str) -> list[float]:
        """Try proxy neural embedding; fall back to local BoW on failure."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float",
            )
            vector = response.data[0].embedding
            # Guard against stub responses: an empty list or all-zeros vector
            # means the endpoint is not implemented on this proxy deployment.
            if vector and any(v != 0.0 for v in vector):
                logger.debug(f"Proxy embedding success (model={self.model})")
                return vector
            logger.warning(
                "Proxy /embeddings returned an empty or zero vector — "
                "falling back to local bag-of-words embedding"
            )
        except Exception as exc:
            logger.warning(
                f"Proxy /embeddings call failed ({exc!r}) — "
                "falling back to local bag-of-words embedding"
            )
        return _local_embed(text)
