"""Tests for src.users — create_user and get_user."""

from unittest.mock import patch

from tests.conftest import fake_get_conn, make_conn, make_cursor


def test_create_user_returns_new_id() -> None:
    cur = make_cursor(fetchone_val=(7,))
    conn = make_conn(cur)
    with patch("src.users.get_conn", return_value=fake_get_conn(conn)):
        from src.users import create_user

        result = create_user("alice", "alice@example.com")
    assert result == 7


def test_create_user_executes_insert() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    with patch("src.users.get_conn", return_value=fake_get_conn(conn)):
        from src.users import create_user

        create_user("bob", "bob@example.com")
    sql = cur.execute.call_args[0][0]
    assert "INSERT INTO users" in sql


def test_create_user_uses_parameterized_query() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    with patch("src.users.get_conn", return_value=fake_get_conn(conn)):
        from src.users import create_user

        create_user("carol", "carol@example.com", "bio text")
    params = cur.execute.call_args[0][1]
    assert params == ("carol", "carol@example.com", "bio text")


def test_create_user_commits() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    with patch("src.users.get_conn", return_value=fake_get_conn(conn)):
        from src.users import create_user

        create_user("dave", "dave@example.com")
    conn.commit.assert_called_once()


def test_get_user_returns_dict_when_found() -> None:
    from datetime import datetime

    ts = datetime(2024, 1, 1)
    cur = make_cursor(fetchone_val=(1, "alice", "alice@example.com", "bio", ts))
    conn = make_conn(cur)
    with patch("src.users.get_conn", return_value=fake_get_conn(conn)):
        from src.users import get_user

        result = get_user(1)
    assert result is not None
    assert result["username"] == "alice"
    assert result["email"] == "alice@example.com"


def test_get_user_returns_none_when_not_found() -> None:
    cur = make_cursor(fetchone_val=None)
    conn = make_conn(cur)
    with patch("src.users.get_conn", return_value=fake_get_conn(conn)):
        from src.users import get_user

        result = get_user(999)
    assert result is None


def test_get_user_queries_by_id() -> None:
    cur = make_cursor(fetchone_val=None)
    conn = make_conn(cur)
    with patch("src.users.get_conn", return_value=fake_get_conn(conn)):
        from src.users import get_user

        get_user(5)
    params = cur.execute.call_args[0][1]
    assert params == (5,)
