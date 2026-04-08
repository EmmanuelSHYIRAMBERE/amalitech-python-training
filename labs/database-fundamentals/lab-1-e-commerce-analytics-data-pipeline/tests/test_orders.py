"""Tests for src.orders — transactional create_order and get_customer_orders."""

from contextlib import contextmanager
from decimal import Decimal
from typing import Any, Generator
from unittest.mock import MagicMock, call, patch

import pytest

from tests.conftest import fake_get_conn, make_conn, make_cursor


def _stock_cursor(stock: int = 10, price: Decimal = Decimal("79.99")) -> MagicMock:
    """Cursor that returns stock/price on first fetchall, then order_id on fetchone."""
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    # fetchall → stock check; fetchone → RETURNING order_id
    cur.fetchall.return_value = [(1, price, stock)]
    cur.fetchone.return_value = (99,)
    return cur


# ── create_order — happy path ─────────────────────────────────────────────────

def test_create_order_returns_order_id() -> None:
    cur = _stock_cursor()
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import create_order
        order_id = create_order(1, [{"product_id": 1, "quantity": 2}])
    assert order_id == 99


def test_create_order_commits_transaction() -> None:
    cur = _stock_cursor()
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import create_order
        create_order(1, [{"product_id": 1, "quantity": 1}])
    conn.commit.assert_called_once()


def test_create_order_decrements_stock() -> None:
    cur = _stock_cursor(stock=5)
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import create_order
        create_order(1, [{"product_id": 1, "quantity": 3}])
    calls = [str(c) for c in cur.execute.call_args_list]
    assert any("UPDATE products" in c for c in calls)


def test_create_order_inserts_order_item() -> None:
    cur = _stock_cursor()
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import create_order
        create_order(1, [{"product_id": 1, "quantity": 2}])
    calls = [str(c) for c in cur.execute.call_args_list]
    assert any("INSERT INTO order_items" in c for c in calls)


# ── create_order — insufficient stock ────────────────────────────────────────

def test_create_order_raises_on_insufficient_stock() -> None:
    cur = _stock_cursor(stock=1)
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import create_order
        with pytest.raises(ValueError, match="Insufficient stock"):
            create_order(1, [{"product_id": 1, "quantity": 5}])


def test_create_order_rolls_back_on_error() -> None:
    cur = _stock_cursor(stock=1)
    conn = make_conn(cur)

    @contextmanager
    def fake_conn_with_rollback() -> Generator[MagicMock, None, None]:
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise

    with patch("src.orders.get_conn", return_value=fake_conn_with_rollback()):
        from src.orders import create_order
        with pytest.raises(ValueError):
            create_order(1, [{"product_id": 1, "quantity": 99}])
    conn.rollback.assert_called_once()


# ── get_customer_orders ───────────────────────────────────────────────────────

def test_get_customer_orders_returns_list() -> None:
    from datetime import datetime
    ts = datetime(2024, 1, 1)
    rows = [(10, "confirmed", ts, 1, 2, Decimal("79.99"))]
    cur = make_cursor(fetchall_val=rows)
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import get_customer_orders
        result = get_customer_orders(1)
    assert len(result) == 1
    assert result[0]["order_id"] == 10
    assert result[0]["status"] == "confirmed"


def test_get_customer_orders_groups_items_by_order() -> None:
    from datetime import datetime
    ts = datetime(2024, 1, 1)
    rows = [
        (10, "confirmed", ts, 1, 2, Decimal("79.99")),
        (10, "confirmed", ts, 2, 1, Decimal("34.99")),
    ]
    cur = make_cursor(fetchall_val=rows)
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import get_customer_orders
        result = get_customer_orders(1)
    assert len(result) == 1
    assert len(result[0]["items"]) == 2


def test_get_customer_orders_returns_empty_for_unknown_customer() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import get_customer_orders
        result = get_customer_orders(999)
    assert result == []


def test_get_customer_orders_unit_price_is_float() -> None:
    from datetime import datetime
    ts = datetime(2024, 1, 1)
    rows = [(10, "confirmed", ts, 1, 1, Decimal("49.99"))]
    cur = make_cursor(fetchall_val=rows)
    conn = make_conn(cur)
    with patch("src.orders.get_conn", return_value=fake_get_conn(conn)):
        from src.orders import get_customer_orders
        result = get_customer_orders(1)
    assert isinstance(result[0]["items"][0]["unit_price"], float)
