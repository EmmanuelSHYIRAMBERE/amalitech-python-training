"""Retrieval-Augmented Generation (RAG) pipeline."""

import json
import logging
import re

from app.exceptions import RateLimitError  # noqa: F401

# Female authors in the current catalogue — used to resolve gender queries.
_FEMALE_AUTHORS = {
    "Jane Austen",
    "Charlotte Brontë",
    "Emily Brontë",
    "Gillian Flynn",
    "Liane Moriarty",
    "Hilary Mantel",
    "Ursula K. Le Guin",
    "Erin Morgenstern",
}

_MALE_AUTHORS = {
    "Frank Herbert", "Andy Weir", "Orson Scott Card", "Isaac Asimov",
    "Stieg Larsson", "Dan Brown", "Umberto Eco", "Ken Follett",
    "Anthony Doerr", "J.R.R. Tolkien", "Patrick Rothfuss",
    "James Clear", "Cal Newport", "Viktor Frankl",
    "Daniel Kahneman", "Eckhart Tolle",
}

_FILTER_SYSTEM = (
    "You are a structured data extractor for a book library search engine.\n"
    "The catalogue has exactly these genres: "
    "Science Fiction, Fantasy, Classic Romance, Crime Thriller, "
    "Historical Fiction, Self-Help.\n"
    "Extract search filters from the user query. "
    "Respond with ONLY a JSON object — no explanation, no markdown.\n"
    "Schema:\n"
    "{\n"
    '  "genre": "<exact genre from list above or null>",\n'
    '  "author_name": "<first name, last name, or partial name if mentioned, else null>",\n'
    '  "author_gender": "<male|female|null>",\n'
    '  "search_keywords": "<5-8 keywords describing the book type, mood, themes>"\n'
    "}\n"
    "Rules:\n"
    "- genre must be exactly one of the listed genres or null.\n"
    "- author_name: extract any name mentioned (e.g. 'Emily' → 'Emily', 'by Daniel' → 'Daniel').\n"
    "- author_gender: set to 'female' for 'female author/writer/woman', "
    "'male' for 'male author/man', null otherwise.\n"
    "- search_keywords: always produce relevant book search terms even for "
    "non-book queries (e.g. 'movie story' → 'narrative fiction drama compelling plot').\n"
    "Examples:\n"
    '  Input:  "Recommend a book by Emily"\n'
    '  Output: {"genre": null, "author_name": "Emily", "author_gender": null, '
    '"search_keywords": "classic romance fiction"}\n'
    '  Input:  "Recommend a book by a female about space"\n'
    '  Output: {"genre": "Science Fiction", "author_name": null, "author_gender": "female", '
    '"search_keywords": "science fiction space exploration female author"}\n'
    '  Input:  "I want a thriller"\n'
    '  Output: {"genre": "Crime Thriller", "author_name": null, "author_gender": null, '
    '"search_keywords": "crime thriller suspense mystery"}'
)

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG pipeline: rewrite → cache → embed → search → generate → cache.

    Before embedding, every query is rewritten by the AI into a compact
    5-10 word search phrase that captures the user's intent.  This means
    vague or conversational queries ("something gripping for a long flight
    with a twist") are distilled into retrieval-friendly terms ("mystery
    thriller suspense plot twist") before hitting the vector store.

    If no results exceed the relevance threshold after the rewrite, a
    polite refusal is returned without a second AI call.

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
            1.  Normalise and check the response cache.
            2.  Acquire a rate-limit token.
            3.  Rewrite the query — AI distils it to search keywords.
            4.  Embed the rewritten query.
            5.  Search the vector store.
            6.  Filter results below the relevance threshold.
            7.  Return a polite refusal if no relevant books found.
            8.  Build a context block from the filtered results.
            9.  Generate an AI answer grounded in the context.
            10. Record token usage.
            11. Cache and return the response.

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

        # Step 4 — Extract structured filters + clean search keywords.
        # The AI parses the question for genre, author name, author gender
        # and a keyword phrase.  Hard constraints become a ChromaDB where
        # filter; the keyword phrase is what gets embedded.
        where_filter, search_keywords = self._extract_filters(question)
        logger.info(f"Search keywords: {search_keywords!r}, filter: {where_filter}")

        # Step 5 — Embed the keyword phrase (not the raw question)
        query_vector = self.embedding_service.embed(search_keywords)

        # Step 6 — Vector search (with optional metadata filter)
        results = self.vector_store.search(query_vector, self.top_k, where=where_filter)

        # Step 7 — Filter by relevance threshold
        relevant = [r for r in results if r["similarity"] >= self.threshold]
        logger.info(
            f"RAG: {len(results)} results, "
            f"{len(relevant)} above threshold {self.threshold}"
        )

        # Log top scores for debugging
        if results:
            top_scores = [(r["title"], round(r["similarity"], 3)) for r in results[:3]]
            logger.info(f"Top scores: {top_scores}")

        # Step 8 — No-context fallback (no hallucination)
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

        # Step 9 — Build context block
        context = self._format_context(relevant)

        # Step 10 — System prompt + generate answer.
        # Pass the original question (not the rewrite) so the AI replies
        # in the same tone and language the user used.
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

    def _rewrite_query(self, question: str) -> str:
        """Distil a user question into compact retrieval keywords.

        Sends the question to the AI with a strict instruction to return
        only 5-10 search keywords that capture the user's intent.  This
        converts vague or conversational phrasing into terms that match
        the vocabulary used in the book catalogue documents.

        Examples::

            "I'm bored and want something exciting for a long flight"
            → "action adventure thriller gripping page-turner"

            "A book like Harry Potter but for adults"
            → "fantasy magic school coming-of-age adult wizard"

        Falls back to the original question unchanged if the AI call
        fails, so the pipeline always continues.

        Args:
            question: The raw user question.

        Returns:
            A short keyword phrase (5-10 words) suitable for embedding
            and vector search, or the original question on error.
        """
        # Cache the rewrite so the same question always maps to the same
        # keywords — avoids non-determinism from the AI proxy and saves a
        # round-trip for repeated queries.
        rewrite_cache_key = f"rewrite:{question.strip().lower()}"
        cached_keywords = self.cache.get(rewrite_cache_key)
        if cached_keywords:
            logger.debug(f"Rewrite cache hit: {cached_keywords!r}")
            return cached_keywords

        system = (
            "You are a search query optimiser for a book library catalogue.\n"
            "The catalogue contains books in these genres: "
            "Science Fiction, Fantasy, Classic Romance, Crime Thriller, "
            "Historical Fiction, Self-Help.\n"
            "Your ONLY job: rewrite the user input into 5-8 keywords that "
            "will match books in this catalogue.\n"
            "Rules:\n"
            "- Output ONLY the keywords, space-separated. No punctuation, "
            "no explanation, no sentences.\n"
            "- If the input mentions something outside books (e.g. movies, "
            "music, food), map it to the closest book equivalent "
            "(e.g. 'movie story' → 'narrative-driven fiction character drama plot').\n"
            "- Always include at least one genre word from the catalogue.\n"
            "- Focus on: genre, themes, mood, setting, narrative style.\n"
            "Examples:\n"
            "  Input:  I want something gripping for a long flight\n"
            "  Output: thriller suspense fast-paced crime mystery\n"
            "  Input:  A book like Harry Potter but for adults\n"
            "  Output: fantasy magic adventure coming-of-age wizard\n"
            "  Input:  Recommend a book about movie story\n"
            "  Output: narrative fiction compelling plot drama story-driven\n"
            "  Input:  space adventure survival\n"
            "  Output: science fiction space survival adventure exploration"
        )
        try:
            keywords = self.ai_service.generate(
                prompt=question,
                system=system,
                temperature=0.0,
                max_tokens=20,
            ).strip()
            if keywords:
                # Cache the rewrite for 1 h so repeated queries are stable
                self.cache.set(rewrite_cache_key, keywords, ttl=3600)
                return keywords
        except Exception as exc:
            logger.warning(f"Query rewrite failed ({exc!r}), using original question")
        return question

    def _extract_filters(self, question: str) -> tuple[dict | None, str]:
        """Extract hard metadata filters and search keywords from a question.

        Uses the AI to parse author name, author gender, genre, and a
        clean keyword phrase from the raw user question.  Returns a
        ChromaDB ``where`` filter dict (or ``None`` if no structural
        constraints were found) and the keyword string to embed.

        Args:
            question: Raw user question.

        Returns:
            Tuple of ``(where_filter, search_keywords)``.
            ``where_filter`` is a ChromaDB-compatible dict or ``None``.
            ``search_keywords`` is always a non-empty string.
        """
        cache_key = f"filters:{question.strip().lower()}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Filter cache hit: {cached}")
            return cached.get("where"), cached.get("keywords", question)

        try:
            raw = self.ai_service.generate(
                prompt=question,
                system=_FILTER_SYSTEM,
                temperature=0.0,
                max_tokens=80,
            ).strip()
            # Strip accidental markdown fences
            clean = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()
            parsed = json.loads(clean)
        except Exception as exc:
            logger.warning(f"Filter extraction failed ({exc!r}), skipping filters")
            return None, question

        genre = parsed.get("genre")
        author_name = parsed.get("author_name")
        author_gender = parsed.get("author_gender")
        keywords = parsed.get("search_keywords") or question

        # Build ChromaDB where clause
        conditions: list[dict] = []

        if genre:
            conditions.append({"genre": {"$eq": genre}})

        if author_name:
            # Match any author whose name contains the extracted fragment
            matched = [
                a for a in (_FEMALE_AUTHORS | _MALE_AUTHORS)
                if author_name.lower() in a.lower()
            ]
            if matched:
                conditions.append({"author": {"$in": matched}})
            else:
                # Unknown author — pass name as keyword instead
                keywords = f"{author_name} {keywords}"

        if author_gender == "female":
            female_list = sorted(_FEMALE_AUTHORS)
            conditions.append({"author": {"$in": female_list}})
        elif author_gender == "male":
            male_list = sorted(_MALE_AUTHORS)
            conditions.append({"author": {"$in": male_list}})

        where: dict | None = None
        if len(conditions) == 1:
            where = conditions[0]
        elif len(conditions) > 1:
            where = {"$and": conditions}

        logger.info(
            f"Filters extracted — genre={genre!r}, author={author_name!r}, "
            f"gender={author_gender!r}, where={where}, keywords={keywords!r}"
        )
        self.cache.set(cache_key, {"where": where, "keywords": keywords}, ttl=3600)
        return where, keywords

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
