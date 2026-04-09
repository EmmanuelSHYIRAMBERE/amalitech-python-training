"""MongoDB shopping-cart session storage."""

import os
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

_client: MongoClient | None = None  # type: ignore[type-arg]


def _sessions() -> Collection:  # type: ignore[type-arg]
    global _client
    if _client is None:
        _client = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017/"))
    return _client["Ecommerce"]["sessions"]


def save_cart(session_id: str, customer_id: int, cart_items: list[dict[str, Any]]) -> None:
    _sessions().replace_one(
        {"session_id": session_id},
        {"session_id": session_id, "customer_id": customer_id, "cart": cart_items},
        upsert=True,
    )


def get_cart(session_id: str) -> dict[str, Any] | None:
    return _sessions().find_one({"session_id": session_id}, {"_id": 0})  # type: ignore[return-value]


def delete_cart(session_id: str) -> None:
    _sessions().delete_one({"session_id": session_id})
