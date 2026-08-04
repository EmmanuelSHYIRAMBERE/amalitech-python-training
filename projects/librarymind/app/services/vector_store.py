"""ChromaDB-backed vector store for book embeddings."""

import logging

import chromadb

logger = logging.getLogger(__name__)


class VectorStore:
    """Persistent ChromaDB collection for semantic book search.

    Uses cosine similarity (``hnsw:space: cosine``).  ChromaDB returns
    cosine *distance* (0 = identical, 2 = opposite), which is converted
    to a similarity score via ``similarity = 1 - distance``.

    Args:
        persist_dir: Filesystem path for ChromaDB persistence.

    Example:
        >>> store = VectorStore("./chroma_db")
        >>> store.upsert("book_001", embedding, "Dune by Frank Herbert", meta)
        >>> results = store.search(query_vec, top_k=3)
    """

    def __init__(self, persist_dir: str = "./chroma_db") -> None:
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="library_books",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"VectorStore ready. " f"Books in collection: {self.collection.count()}"
        )

    def upsert(
        self,
        book_id: str,
        embedding: list[float],
        document: str,
        metadata: dict,
    ) -> None:
        """Insert or update a book in the collection.

        Args:
            book_id: Unique string identifier (e.g. ``"book_001"``).
            embedding: Pre-computed embedding vector.
            document: Raw text that was embedded (stored for retrieval).
            metadata: Dict of scalar fields stored alongside the vector
                (e.g. ``title``, ``author``, ``genre``, ``year``).
        """
        self.collection.upsert(
            ids=[book_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata],
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict | None = None,
    ) -> list[dict]:
        """Return the top-k most similar books for a query vector.

        Args:
            query_embedding: Query vector of the same dimensionality
                as the stored embeddings.
            top_k: Maximum number of results to return.
            where: Optional ChromaDB metadata filter (e.g.
                ``{"genre": "Fantasy"}`` or
                ``{"author": {"$in": ["Jane Austen", "Emily Brontë"]}}``).
                When provided, only books matching the filter are searched.

        Returns:
            List of dicts, each containing all metadata fields plus
            ``"document"`` and ``"similarity"`` (float, higher = more
            similar).  Sorted by descending similarity.
        """
        # ChromaDB requires n_results ≤ number of matching documents.
        # When a where filter is active the matching set may be smaller
        # than top_k — query up to the full collection and cap afterwards.
        safe_k = min(top_k, self.collection.count()) or 1
        kwargs: dict = dict(
            query_embeddings=[query_embedding],
            n_results=safe_k,
            include=["documents", "metadatas", "distances"],
        )
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)
        output = []
        for i, meta in enumerate(results["metadatas"][0]):
            # ChromaDB cosine DISTANCE → convert to similarity score
            # distance=0 means identical, distance=2 means opposite
            similarity = 1.0 - results["distances"][0][i]
            output.append(
                {
                    **meta,
                    "document": results["documents"][0][i],
                    "similarity": similarity,
                }
            )
        output.sort(key=lambda x: x["similarity"], reverse=True)
        return output[:top_k]

    def count(self) -> int:
        """Return the number of documents stored in the collection.

        Returns:
            Integer count of records currently in ChromaDB.
        """
        return self.collection.count()
