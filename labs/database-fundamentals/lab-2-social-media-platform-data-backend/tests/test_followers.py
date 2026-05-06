"""Tests for src.followers — follow_user, unfollow_user, get_following, get_followers."""

from unittest.mock import patch

import pytest

from tests.conftest import fake_get_conn, make_conn, make_cursor


def test_follow_user_inserts_row() -> None:
    cur = make_cursor()
    conn = make_conn(cur)
    with patch("src.followers.get_conn", return_value=fake_get_conn(conn)):
        from src.followers import follow_user

        follow_user(1, 2)
    sql = cur.execute.call_args[0][0]
    assert "INSERT INTO followers" in sql


def test_follow_user_uses_parameterized_query() -> None:
    cur = make_cursor()
    conn = make_conn(cur)
    with patch("src.followers.get_conn", return_value=fake_get_conn(conn)):
        from src.followers import follow_user

        follow_user(1, 2)
    params = cur.execute.call_args[0][1]
    assert params == (1, 2)


def test_follow_user_commits() -> None:
    cur = make_cursor()
    conn = make_conn(cur)
    with patch("src.followers.get_conn", return_value=fake_get_conn(conn)):
        from src.followers import follow_user

        follow_user(1, 2)
    conn.commit.assert_called_once()


def test_follow_user_raises_on_self_follow() -> None:
    with pytest.raises(ValueError, match="cannot follow themselves"):
        from src.followers import follow_user

        follow_user(1, 1)


def test_unfollow_user_deletes_row() -> None:
    cur = make_cursor()
    conn = make_conn(cur)
    with patch("src.followers.get_conn", return_value=fake_get_conn(conn)):
        from src.followers import unfollow_user

        unfollow_user(1, 2)
    sql = cur.execute.call_args[0][0]
    assert "DELETE FROM followers" in sql


def test_unfollow_user_uses_parameterized_query() -> None:
    cur = make_cursor()
    conn = make_conn(cur)
    with patch("src.followers.get_conn", return_value=fake_get_conn(conn)):
        from src.followers import unfollow_user

        unfollow_user(3, 4)
    params = cur.execute.call_args[0][1]
    assert params == (3, 4)


def test_get_following_returns_list() -> None:
    cur = make_cursor(fetchall_val=[(2, "bob"), (3, "carol")])
    conn = make_conn(cur)
    with patch("src.followers.get_conn", return_value=fake_get_conn(conn)):
        from src.followers import get_following

        result = get_following(1)
    assert len(result) == 2
    assert result[0]["username"] == "bob"


def test_get_followers_returns_list() -> None:
    cur = make_cursor(fetchall_val=[(4, "dave")])
    conn = make_conn(cur)
    with patch("src.followers.get_conn", return_value=fake_get_conn(conn)):
        from src.followers import get_followers

        result = get_followers(1)
    assert len(result) == 1
    assert result[0]["username"] == "dave"


def test_get_following_returns_empty_for_no_follows() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.followers.get_conn", return_value=fake_get_conn(conn)):
        from src.followers import get_following

        result = get_following(99)
    assert result == []
