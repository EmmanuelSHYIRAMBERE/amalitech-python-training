"""Tests for src.analytics — window functions, CTE revenue, EXPLAIN ANALYZE."""

from decimal import Decimal
from unittest.mock import patch

from tests.conftest import fake_get_conn, make_conn, make_cursor


# ── rank_products_by_category ─────────────────────────────────────────────────

def test_rank_products_returns_list_of_dicts() -> None:
    rows = [("Electronics", "Headphones", 50, 1)]
    cur = make_cursor(fetchall_val=rows)
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import rank_products_by_category
        result = rank_products_by_category()
    assert isinstance(result, list)
    assert result[0] == {"category": "Electronics", "product": "Headphones", "units_sold": 50, "rank": 1}


def test_rank_products_uses_rank_window_function() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import rank_products_by_category
        rank_products_by_category()
    sql = cur.execute.call_args[0][0]
    assert "RANK()" in sql
    assert "PARTITION BY" in sql


def test_rank_products_returns_empty_list_when_no_data() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import rank_products_by_category
        result = rank_products_by_category()
    assert result == []


# ── revenue_per_customer ──────────────────────────────────────────────────────

def test_revenue_per_customer_returns_list_of_dicts() -> None:
    rows = [(1, "Alice", Decimal("159.98"))]
    cur = make_cursor(fetchall_val=rows)
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import revenue_per_customer
        result = revenue_per_customer()
    assert result[0] == {"customer_id": 1, "name": "Alice", "total_revenue": 159.98}


def test_revenue_per_customer_total_revenue_is_float() -> None:
    rows = [(1, "Alice", Decimal("99.99"))]
    cur = make_cursor(fetchall_val=rows)
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import revenue_per_customer
        result = revenue_per_customer()
    assert isinstance(result[0]["total_revenue"], float)


def test_revenue_per_customer_uses_cte() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import revenue_per_customer
        revenue_per_customer()
    sql = cur.execute.call_args[0][0]
    assert "WITH" in sql
    assert "order_totals" in sql


def test_revenue_per_customer_returns_empty_list_when_no_data() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import revenue_per_customer
        result = revenue_per_customer()
    assert result == []


# ── explain_customer_orders ───────────────────────────────────────────────────

def test_explain_returns_string() -> None:
    cur = make_cursor(fetchall_val=[("Seq Scan on orders",), ("Planning Time: 0.1 ms",)])
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import explain_customer_orders
        result = explain_customer_orders(1)
    assert isinstance(result, str)


def test_explain_joins_lines_with_newline() -> None:
    cur = make_cursor(fetchall_val=[("line one",), ("line two",)])
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import explain_customer_orders
        result = explain_customer_orders(1)
    assert result == "line one\nline two"


def test_explain_uses_explain_analyze_sql() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.analytics.get_conn", return_value=fake_get_conn(conn)):
        from src.analytics import explain_customer_orders
        explain_customer_orders(1)
    sql = cur.execute.call_args[0][0]
    assert "EXPLAIN ANALYZE" in sql
    assert "customer_id" in sql
