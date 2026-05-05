"""MongoDB activity stream — stores unstructured user action events."""

import os
from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

_client: MongoClient | None = None  # type: ignore[type-arg]


def _activity() -> Collection:  # type: ignore[type-arg]
    global _client
    if _client is None:
        _client = MongoClient(os.getenv("MONGO_URL", "mongodb://127.0.0.1:27018/"))
    return _client["social"]["activity"]


def log_activity(actor_id: int, action: str, target: dict[str, Any]) -> None:
    """
    Log an activity event.
    action examples: 'liked_post', 'followed_user', 'commented_on_post'
    target examples: {'post_id': 3}, {'user_id': 2}
    """
    _activity().insert_one(
        {
            "actor_id": actor_id,
            "action": action,
            "target": target,
            "timestamp": datetime.now(timezone.utc),
        }
    )


def get_activity(actor_id: int, limit: int = 20) -> list[dict[str, Any]]:
    cursor = _activity().find({"actor_id": actor_id}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return list(cursor)
