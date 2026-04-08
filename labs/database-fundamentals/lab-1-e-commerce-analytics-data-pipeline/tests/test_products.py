"""Tests for src.products — CRUD, Redis cache, and JSONB metadata query."""

import json
from unittest.mock import patch

import pytest

from tests.conftest import fake_get_conn, make_conn, make_cursor


# ── add_product ───────────────────────────────────────────────────────────────

def test_add_product_returns_new_id(mock_redis: object) -> None:
    cur = make_cursor(fetchone_val=(10,))
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)), \
         patch("src.products._redis", mock_redis):
        from src.products import add_product
        result = add_product(1, "Headphones", 79.99, 50, {"color": "black"})
    assert result == 10


def test_add_product_invalidates_redis_cache(mock_redis: object) -> None:
    cur = make_cursor(fetchone_val=(10,))
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)), \
         patch("src.products._redis", mock_redis):
        from src.products import add_product
        add_product(1, "Headphones", 79.99, 50, {"color": "black"})
    mock_redis.delete.assert_called_once_with("top10_products")  # type: ignore[attr-defined]


def test_add_product_serializes_metadata_as_json(mock_redis: object) -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    metadata = {"color": "black", "wireless": True}
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)), \
         patch("src.products._redis", mock_redis):
        from src.products import add_product
        add_product(1, "Headphones", 79.99, 50, metadata)
    params = cur.execute.call_args[0][1]
    assert params[4] == json.dumps(metadata)


# ── get_product ───────────────────────────────────────────────────────────────

def test_get_product_returns_dict_when_found() -> None:
    from decimal import Decimal
    cur = make_cursor(fetchone_val=(1, 2, "Headphones", Decimal("79.99"), 50, {"color": "black"}))
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)):
        from src.products import get_product
        result = get_product(1)
    assert result is not None
    assert result["product_id"] == 1
    assert result["price"] == 79.99
    assert isinstance(result["price"], float)


def test_get_product_returns_none_when_not_found() -> None:
    cur = make_cursor(fetchone_val=None)
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)):
        from src.products import get_product
        result = get_product(999)
    assert result is None


# ── get_top10_best_sellers ────────────────────────────────────────────────────

def test_top10_returns_cached_result_without_db_query(mock_redis: object) -> None:
    cached = [{"product_id": 1, "name": "A", "units_sold": 100}]
    mock_redis.get.return_value = json.dumps(cached)  # type: ignore[attr-defined]
    with patch("src.products._redis", mock_redis):
        from src.products import get_top10_best_sellers
        result = get_top10_best_sellers()
    assert result == cached


def test_top10_queries_db_on_cache_miss(mock_redis: object) -> None:
    mock_redis.get.return_value = None  # type: ignore[attr-defined]
    cur = make_cursor(fetchall_val=[(1, "Headphones", 50)])
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)), \
         patch("src.products._redis", mock_redis):
        from src.products import get_top10_best_sellers
        result = get_top10_best_sellers()
    assert result[0]["name"] == "Headphones"
    assert result[0]["units_sold"] == 50


def test_top10_stores_result_in_redis_after_db_query(mock_redis: object) -> None:
    mock_redis.get.return_value = None  # type: ignore[attr-defined]
    cur = make_cursor(fetchall_val=[(1, "Headphones", 50)])
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)), \
         patch("src.products._redis", mock_redis):
        from src.products import get_top10_best_sellers
        get_top10_best_sellers()
    mock_redis.setex.assert_called_once()  # type: ignore[attr-defined]
    key, ttl, _ = mock_redis.setex.call_args[0]  # type: ignore[attr-defined]
    assert key == "top10_products"
    assert ttl == 300


# ── find_products_by_metadata ─────────────────────────────────────────────────

def test_find_by_metadata_returns_matching_products() -> None:
    cur = make_cursor(fetchall_val=[(1, "Headphones", {"color": "black", "wireless": True})])
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)):
        from src.products import find_products_by_metadata
        result = find_products_by_metadata("wireless", True)
    assert len(result) == 1
    assert result[0]["name"] == "Headphones"


def test_find_by_metadata_uses_jsonb_contains_operator() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)):
        from src.products import find_products_by_metadata
        find_products_by_metadata("color", "black")
    sql = cur.execute.call_args[0][0]
    assert "@>" in sql


def test_find_by_metadata_returns_empty_list_when_no_match() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.products.get_conn", return_value=fake_get_conn(conn)):
        from src.products import find_products_by_metadata
        result = find_products_by_metadata("color", "pink")
    assert result == []
