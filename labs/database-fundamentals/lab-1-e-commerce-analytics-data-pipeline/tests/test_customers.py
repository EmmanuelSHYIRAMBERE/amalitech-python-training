"""Tests for src.customers — add_customer and get_customer."""

from unittest.mock import patch

from tests.conftest import fake_get_conn, make_conn, make_cursor

# ── add_customer ──────────────────────────────────────────────────────────────


def test_add_customer_returns_new_id() -> None:
    cur = make_cursor(fetchone_val=(42,))
    conn = make_conn(cur)
    with patch("src.customers.get_conn", return_value=fake_get_conn(conn)):
        from src.customers import add_customer

        result = add_customer("Alice", "alice@example.com")
    assert result == 42


def test_add_customer_executes_insert() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    with patch("src.customers.get_conn", return_value=fake_get_conn(conn)):
        from src.customers import add_customer

        add_customer("Bob", "bob@example.com")
    sql = cur.execute.call_args[0][0]
    assert "INSERT INTO customers" in sql


def test_add_customer_uses_parameterized_query() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    with patch("src.customers.get_conn", return_value=fake_get_conn(conn)):
        from src.customers import add_customer

        add_customer("Carol", "carol@example.com")
    params = cur.execute.call_args[0][1]
    assert params == ("Carol", "carol@example.com")


def test_add_customer_commits_transaction() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    with patch("src.customers.get_conn", return_value=fake_get_conn(conn)):
        from src.customers import add_customer

        add_customer("Dave", "dave@example.com")
    conn.commit.assert_called_once()


# ── get_customer ──────────────────────────────────────────────────────────────


def test_get_customer_returns_dict_when_found() -> None:
    from datetime import datetime

    ts = datetime(2024, 1, 1)
    cur = make_cursor(fetchone_val=(7, "Alice", "alice@example.com", ts))
    conn = make_conn(cur)
    with patch("src.customers.get_conn", return_value=fake_get_conn(conn)):
        from src.customers import get_customer

        result = get_customer(7)
    assert result == {
        "customer_id": 7,
        "name": "Alice",
        "email": "alice@example.com",
        "created_at": ts,
    }


def test_get_customer_returns_none_when_not_found() -> None:
    cur = make_cursor(fetchone_val=None)
    conn = make_conn(cur)
    with patch("src.customers.get_conn", return_value=fake_get_conn(conn)):
        from src.customers import get_customer

        result = get_customer(999)
    assert result is None


def test_get_customer_queries_by_id() -> None:
    cur = make_cursor(fetchone_val=None)
    conn = make_conn(cur)
    with patch("src.customers.get_conn", return_value=fake_get_conn(conn)):
        from src.customers import get_customer

        get_customer(5)
    params = cur.execute.call_args[0][1]
    assert params == (5,)
