#!/usr/bin/env python3
"""
Seed script — populates ChromaDB with books from data/books.json.
Run from project root: python scripts/seed.py
"""

# sys.path manipulation must happen before project imports.
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx  # noqa: E402
import openai  # noqa: E402
from app.config import settings  # noqa: E402
from app.infrastructure.cache import CacheService  # noqa: E402
from app.services.embedding import EmbeddingService  # noqa: E402
from app.services.vector_store import VectorStore  # noqa: E402


def main():
    books_path = Path(__file__).parent.parent / "data" / "books.json"
    books = json.loads(books_path.read_text(encoding="utf-8"))

    # openai SDK pointed at Amalitec proxy with SSL verification disabled.
    # The EmbeddingService uses local numpy embeddings (proxy /embeddings
    # is a stub), but the client is passed through for interface compatibility.
    openai_client = openai.OpenAI(
        api_key=settings.AMALI_API_KEY,
        base_url=settings.AMALI_BASE_URL,
        http_client=httpx.Client(verify=False),
    )
    cache = CacheService(settings.REDIS_URL, settings.CACHE_TTL_SECONDS)
    embedding_service = EmbeddingService(openai_client, cache, settings.EMBEDDING_MODEL)
    vector_store = VectorStore(settings.CHROMA_DB_PATH)

    print(f"Seeding {len(books)} books into ChromaDB...")
    for book in books:
        # Include genre and author prominently so bag-of-words similarity
        # picks up genre-specific queries reliably.
        text = (
            f"{book['title']} by {book['author']}. "
            f"Genre: {book['genre']}. "
            f"{book['description']} "
            f"Genre: {book['genre']}. Author: {book['author']}."
        )
        embedding = embedding_service.embed(text)
        vector_store.upsert(
            book_id=book["id"],
            embedding=embedding,
            document=text,
            metadata={
                "title": book["title"],
                "author": book["author"],
                "year": book["year"],
                "genre": book["genre"],
                "book_id": book["id"],
            },
        )
        print(f"  [OK] {book['title']}")

    print(f"\nTotal books in vector store: {vector_store.count()}")


if __name__ == "__main__":
    main()
