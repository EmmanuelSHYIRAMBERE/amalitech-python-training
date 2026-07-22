"""Local numpy bag-of-words embedding service.

The Amalitec proxy ``/embeddings`` endpoint is a stub (empty 200) and
all external model downloads (ChromaDB ONNX, tiktoken) are blocked by
the corporate SSL proxy.  This module provides a fully local,
deterministic, dependency-free embedding that is API-compatible with
the OpenAI embeddings interface so it can be swapped out when the proxy
adds real embedding support.
"""

import hashlib
import logging
import struct
from typing import Any

import numpy as np

from app.infrastructure.cache import CacheService

logger = logging.getLogger(__name__)

# Embedding dimensionality matches text-embedding-3-small for drop-in
# compatibility once the proxy adds a real /embeddings endpoint.
_DIMS = 1536


def _word_vector(word: str) -> np.ndarray:
    """Map a single word to a deterministic unit vector in _DIMS-space.

    Uses SHA-256 of the word to seed a numpy RNG, then draws a
    standard-normal vector and L2-normalises it.  Identical words
    always produce identical vectors; different words produce nearly
    orthogonal vectors (expected cosine ≈ 0).

    Args:
        word: Lowercase word token to embed.

    Returns:
        Float32 numpy array of shape ``(_DIMS,)`` with unit L2-norm.
    """
    digest = hashlib.sha256(word.encode()).digest()
    seed = struct.unpack("<Q", digest[:8])[0]
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(_DIMS).astype(np.float32)
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


def _local_embed(text: str) -> list[float]:
    """Bag-of-words embedding: sum the unit word vectors then L2-normalise.

    Properties:
    - Deterministic: same text → same vector every time
    - Symmetric: order-independent (bag of words)
    - Semantic proximity: texts sharing words have higher cosine similarity
    - Dimension: ``_DIMS`` (1536) floats, unit-norm

    Args:
        text: Raw text to embed (case-insensitive; split on whitespace).

    Returns:
        List of ``_DIMS`` floats representing the unit-normalised
        bag-of-words vector.  Returns a zero vector for empty input.
    """
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


class EmbeddingService:
    """Generates text embeddings with Redis caching.

    The ``openai_client`` parameter is accepted for API compatibility with
    the Phase 3 spec (and for future use when the proxy supports
    ``/embeddings``), but the actual computation uses the local
    :func:`_local_embed` function.  Cached embeddings are stored for 24 h.

    Args:
        openai_client: Reserved for proxy-backed embedding (unused now).
        cache: Cache service used to persist computed embeddings.
        model: Embedding model name (used as part of the cache key).

    Example:
        >>> svc = EmbeddingService(client, cache)
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
        self.client = openai_client  # kept for interface compatibility
        self.cache = cache
        self.model = model

    def embed(self, text: str) -> list[float]:
        """Return the embedding vector for a single text string.

        Checks the cache first; on a miss computes locally and stores
        the result for 24 hours.

        Args:
            text: Text to embed.

        Returns:
            List of ``_DIMS`` floats (unit-normalised).
        """
        cache_key = f"emb:{self.model}:{text}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug("Embedding cache hit")
            return cached

        vector = _local_embed(text)
        self.cache.set(cache_key, vector, ttl=86400)
        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts, each cached independently.

        Args:
            texts: List of strings to embed.

        Returns:
            List of embedding vectors in the same order as ``texts``.
        """
        return [self.embed(t) for t in texts]
