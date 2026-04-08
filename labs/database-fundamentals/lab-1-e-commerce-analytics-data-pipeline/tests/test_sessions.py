"""Tests for src.sessions — MongoDB cart session storage."""

from unittest.mock import patch

import pytest


# ── save_cart ─────────────────────────────────────────────────────────────────

def test_save_cart_calls_replace_one(mock_collection: object) -> None:
    with patch("src.sessions._sessions", return_value=mock_collection):
        from src.sessions import save_cart
        save_cart("sess-1", 42, [{"product_id": 1, "quantity": 2}])
    mock_collection.replace_one.assert_called_once()  # type: ignore[attr-defined]


def test_save_cart_uses_upsert(mock_collection: object) -> None:
    with patch("src.sessions._sessions", return_value=mock_collection):
        from src.sessions import save_cart
        save_cart("sess-1", 42, [])
    _, kwargs = mock_collection.replace_one.call_args  # type: ignore[attr-defined]
    assert kwargs.get("upsert") is True


def test_save_cart_stores_correct_session_id(mock_collection: object) -> None:
    with patch("src.sessions._sessions", return_value=mock_collection):
        from src.sessions import save_cart
        save_cart("sess-abc", 1, [])
    filter_doc = mock_collection.replace_one.call_args[0][0]  # type: ignore[attr-defined]
    assert filter_doc == {"session_id": "sess-abc"}


def test_save_cart_stores_customer_id_and_items(mock_collection: object) -> None:
    items = [{"product_id": 3, "quantity": 1}]
    with patch("src.sessions._sessions", return_value=mock_collection):
        from src.sessions import save_cart
        save_cart("sess-xyz", 7, items)
    replacement = mock_collection.replace_one.call_args[0][1]  # type: ignore[attr-defined]
    assert replacement["customer_id"] == 7
    assert replacement["cart"] == items


# ── get_cart ──────────────────────────────────────────────────────────────────

def test_get_cart_returns_document_when_found(mock_collection: object) -> None:
    expected = {"session_id": "sess-1", "customer_id": 1, "cart": []}
    mock_collection.find_one.return_value = expected  # type: ignore[attr-defined]
    with patch("src.sessions._sessions", return_value=mock_collection):
        from src.sessions import get_cart
        result = get_cart("sess-1")
    assert result == expected


def test_get_cart_returns_none_when_not_found(mock_collection: object) -> None:
    mock_collection.find_one.return_value = None  # type: ignore[attr-defined]
    with patch("src.sessions._sessions", return_value=mock_collection):
        from src.sessions import get_cart
        result = get_cart("missing-session")
    assert result is None


def test_get_cart_excludes_mongo_id(mock_collection: object) -> None:
    mock_collection.find_one.return_value = None  # type: ignore[attr-defined]
    with patch("src.sessions._sessions", return_value=mock_collection):
        from src.sessions import get_cart
        get_cart("sess-1")
    projection = mock_collection.find_one.call_args[0][1]  # type: ignore[attr-defined]
    assert projection == {"_id": 0}


# ── delete_cart ───────────────────────────────────────────────────────────────

def test_delete_cart_calls_delete_one(mock_collection: object) -> None:
    with patch("src.sessions._sessions", return_value=mock_collection):
        from src.sessions import delete_cart
        delete_cart("sess-1")
    mock_collection.delete_one.assert_called_once_with({"session_id": "sess-1"})  # type: ignore[attr-defined]
