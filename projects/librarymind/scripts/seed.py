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

    # OpenAI SDK pointed at the Amalitec proxy with SSL verification disabled.
    # EmbeddingService tries the proxy /embeddings endpoint first (neural model)
    # and falls back to local bag-of-words if the proxy returns a stub response.
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
        # Structured opening sentence (title, author, year, genre) followed by
        # the full description.  The structured prefix gives both keyword queries
        # ("science fiction") and natural-language queries ("books about space")
        # explicit anchors; the description provides thematic vocabulary.
        text = (
            f"Book titled \"{book['title']}\" written by {book['author']}, "
            f"published in {book['year']}, genre: {book['genre']}. "
            f"{book['description']}"
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
