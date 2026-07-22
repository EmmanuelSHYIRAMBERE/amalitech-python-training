"""Multi-turn conversational chatbot service."""

import logging

logger = logging.getLogger(__name__)


class ChatbotService:
    """RAG-grounded multi-turn library chatbot with per-session memory.

    Each conversation is identified by a string ``conversation_id``.
    History is kept in memory and truncated to ``max_history`` messages
    (always in user/assistant pairs so turns remain aligned).

    Args:
        rag_engine: Used to retrieve relevant book context for each turn.
        ai_service: Resilient AI service for generating replies.
        max_history: Maximum number of messages (user + assistant) to
            retain per session.  Older pairs are dropped from the front.

    Example:
        >>> bot = ChatbotService(rag_engine, ai_service)
        >>> r = bot.chat("sess-1", "Recommend a thriller")
        >>> print(r["reply"])
        >>> r2 = bot.chat("sess-1", "Tell me more about that one")
        >>> print(r2["reply"])   # elaborates on the previous recommendation
    """

    def __init__(self, rag_engine, ai_service, max_history: int = 10) -> None:
        self.rag_engine = rag_engine
        self.ai_service = ai_service
        self.max_history = max_history
        # In-memory conversation store: {conversation_id: [messages]}
        self.store: dict[str, list[dict]] = {}

    def chat(self, conversation_id: str, message: str) -> dict:
        """Process one user turn and return the assistant's reply.

        Retrieves RAG context for the message, builds a prompt that
        includes prior conversation history, generates a reply, appends
        both turns to the session history, and trims old pairs if needed.

        Args:
            conversation_id: Unique session identifier.  A new session
                is created automatically on first use.
            message: The user's message for this turn.

        Returns:
            Dict with keys:
              - ``"reply"`` (str): The assistant's response.
              - ``"sources"`` (list[dict]): Book sources from RAG.
              - ``"conversation_id"`` (str): Echo of the session ID.

        Raises:
            RateLimitError: Propagated from the RAG engine or AI service.
            RuntimeError: If all AI providers fail.
        """
        # Step 1 — Load or create history for this conversation
        history = self.store.setdefault(conversation_id, [])

        # Step 2 — RAG context for this message
        rag_result = self.rag_engine.answer(message)
        sources = rag_result["sources"]
        context_block = self._format_sources(sources)

        # Step 3 — System prompt
        system = (
            "You are Alexandra, a warm and knowledgeable public "
            "library assistant.\n"
            "Help patrons discover books they will love. "
            "Be friendly, enthusiastic, and personal.\n"
            "Ground every book recommendation in the LIBRARY "
            "CATALOGUE CONTEXT when it is provided.\n"
            "Never fabricate book titles, authors, or publication "
            "years.\n"
            "If the context is empty, you may still converse "
            "naturally but must not invent books.\n"
            "Keep responses concise — 2 to 4 sentences unless "
            "more detail is requested."
        )

        # Step 4 — Build full prompt: history + context + new message
        full_prompt = self._build_prompt(history, message, context_block)

        # Step 5 — Generate reply
        reply = self.ai_service.generate(
            prompt=full_prompt,
            system=system,
            temperature=0.7,
            max_tokens=600,
        )

        # Step 6 — Append both turns to history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})

        # Step 7 — Truncate to max_history in PAIRS
        # Always remove whole pairs (user+assistant) from the front
        if len(history) > self.max_history:
            trimmed = history[-self.max_history :]
            # If the first message is an assistant turn, drop it
            # so we always start on a user turn
            if trimmed and trimmed[0]["role"] == "assistant":
                trimmed = trimmed[1:]
            self.store[conversation_id] = trimmed
        else:
            self.store[conversation_id] = history

        return {
            "reply": reply,
            "sources": sources,
            "conversation_id": conversation_id,
        }

    def _build_prompt(
        self,
        history: list[dict],
        new_message: str,
        context_block: str,
    ) -> str:
        """Build the full prompt from history, context, and new message.

        Format::

            USER: <turn 1>

            ASSISTANT: <turn 1>

            [LIBRARY CATALOGUE CONTEXT]
            - "Title" by Author (Genre)

            USER: <new message>

        Args:
            history: Prior turns as ``[{"role": ..., "content": ...}]``.
            new_message: The current user input.
            context_block: Formatted source list from RAG (may be empty).

        Returns:
            Single string to pass as the ``prompt`` argument to
            :meth:`~app.providers.base.AIProvider.generate`.
        """
        parts = []
        for msg in history:
            parts.append(f'{msg["role"].upper()}: {msg["content"]}')
        if context_block:
            parts.append(f"[LIBRARY CATALOGUE CONTEXT]\n{context_block}")
        parts.append(f"USER: {new_message}")
        return "\n\n".join(parts)

    def _format_sources(self, sources: list[dict]) -> str:
        """Convert a list of source dicts to a bullet-list string.

        Args:
            sources: List of book dicts (must have ``title``, ``author``,
                ``genre`` keys).

        Returns:
            Multi-line bullet string, or empty string if no sources.
        """
        if not sources:
            return ""
        return "\n".join(
            f'- "{s["title"]}" by {s["author"]} ({s["genre"]})' for s in sources
        )
