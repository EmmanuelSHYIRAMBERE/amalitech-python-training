"""Retrieval-Augmented Generation (RAG) pipeline."""

import logging

from app.exceptions import RateLimitError  # noqa: F401

logger = logging.getLogger(__name__)


class RAGEngine:
    """12-step RAG pipeline: cache → embed → search → generate → cache.

    Grounds every AI answer in book metadata retrieved from the vector
    store.  If no results exceed the relevance threshold, returns a
    polite refusal without invoking the AI at all.

    Args:
        embedding_service: Converts text to embedding vectors.
        vector_store: Performs nearest-neighbour search over books.
        ai_service: Resilient AI service for text generation.
        cache: Response cache (no-op when Redis is unavailable).
        rate_limiter: Token-bucket limiter; raises on exhaustion.
        usage_tracker: Records token counts and cost estimates.
        threshold: Minimum cosine similarity to include a result.
            Calibrated at 0.05 for the local bag-of-words model.
        top_k: Maximum number of vector search results to retrieve.

    Example:
        >>> engine = RAGEngine(embedding_service, vector_store,
        ...                    ai_service, cache, rate_limiter,
        ...                    usage_tracker)
        >>> result = engine.answer("What sci-fi books do you have?")
        >>> print(result["answer"])
        >>> print(result["sources"])
    """

    def __init__(
        self,
        embedding_service,
        vector_store,
        ai_service,
        cache,
        rate_limiter,
        usage_tracker,
        threshold: float = 0.05,
        top_k: int = 5,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.ai_service = ai_service
        self.cache = cache
        self.rate_limiter = rate_limiter
        self.usage_tracker = usage_tracker
        self.threshold = threshold
        self.top_k = top_k

    def answer(self, question: str) -> dict:
        """Answer a natural-language question using RAG.

        Steps:
            1. Normalise and check the response cache.
            2. Acquire a rate-limit token.
            3. Embed the question.
            4. Search the vector store.
            5. Filter results below the relevance threshold.
            6. Return a polite refusal if no relevant books found.
            7. Build a context block from the filtered results.
            8. Generate an AI answer grounded in the context.
            9. Record token usage.
            10. Cache and return the response.

        Args:
            question: The user's natural-language question.

        Returns:
            Dict with keys ``"answer"`` (str), ``"sources"`` (list of
            dicts with title/author/genre/similarity), and ``"cached"``
            (bool).

        Raises:
            RateLimitError: When the rate-limit bucket is empty.
            RuntimeError: When all AI providers fail.
        """
        # Step 1 — Normalise for cache key
        cache_key = question.strip().lower()

        # Step 2 — Cache check
        cached = self.cache.get(cache_key)
        if cached:
            logger.info("RAG cache hit")
            return {**cached, "cached": True}

        # Step 3 — Rate limit
        self.rate_limiter.acquire()

        # Step 4 — Embed question
        query_vector = self.embedding_service.embed(question)

        # Step 5 — Vector search
        results = self.vector_store.search(query_vector, self.top_k)

        # Step 6 — Filter by relevance threshold
        relevant = [r for r in results if r["similarity"] >= self.threshold]
        logger.info(
            f"RAG: {len(results)} results, "
            f"{len(relevant)} above threshold {self.threshold}"
        )

        # Log top scores for debugging
        if results:
            top_scores = [(r["title"], round(r["similarity"], 3)) for r in results[:3]]
            logger.info(f"Top scores: {top_scores}")

        # Step 7 — No-context fallback (no hallucination)
        if not relevant:
            return {
                "answer": (
                    "I'm sorry, I couldn't find relevant information "
                    "about that in our library catalogue. Please try a "
                    "different question or ask about our book collection."
                ),
                "sources": [],
                "cached": False,
            }

        # Step 8 — Build context block
        context = self._format_context(relevant)

        # Step 9 — System prompt
        system = (
            "You are a knowledgeable library assistant.\n"
            "Answer ONLY using the book information provided in the "
            "CONTEXT below.\n"
            "Always cite the book title when you reference it "
            "(use quotation marks around titles).\n"
            "If the context does not contain enough information to "
            "fully answer the question, say so clearly — do not invent "
            "books, authors, or facts.\n"
            "Be helpful, concise, and friendly."
        )
        prompt = f"CONTEXT:\n{context}\n\nQUESTION: {question}"

        # Step 10 — Generate answer
        answer_text = self.ai_service.generate(
            prompt=prompt,
            system=system,
            temperature=0.3,
            max_tokens=500,
        )

        # Step 11 — Record usage (token count estimated by word count;
        # tiktoken cannot download its vocab on this network)
        prompt_tokens = len((system + prompt).split()) * 4 // 3
        completion_tokens = len(answer_text.split()) * 4 // 3
        self.usage_tracker.record(
            model=self.ai_service.primary_provider_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            endpoint="/search/ask",
        )

        # Step 12 — Cache and return
        response = {
            "answer": answer_text,
            "sources": [
                {
                    "title": r["title"],
                    "author": r["author"],
                    "genre": r["genre"],
                    "similarity": round(r["similarity"], 3),
                }
                for r in relevant
            ],
        }
        self.cache.set(cache_key, response)
        return {**response, "cached": False}

    def _format_context(self, books: list[dict]) -> str:
        """Format a list of book dicts into a plain-text context block.

        Args:
            books: List of book dicts from the vector store (must contain
                ``title``, ``author``, ``year``, ``genre``, ``document``).

        Returns:
            Multi-line string with one book per line.
        """
        return "\n".join(
            f'- "{b["title"]}" by {b["author"]} '
            f'({b["year"]}, {b["genre"]}): {b["document"]}'
            for b in books
        )
