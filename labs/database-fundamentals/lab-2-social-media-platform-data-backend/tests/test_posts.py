"""Tests for src.posts — create_post, get_post, add_comment, find_posts_by_tag."""

import json
from unittest.mock import patch

from tests.conftest import fake_get_conn, make_conn, make_cursor


def test_create_post_returns_new_id() -> None:
    cur = make_cursor(fetchone_val=(3,))
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import create_post

        result = create_post(1, "Hello world!", {"tags": ["python"]})
    assert result == 3


def test_create_post_serializes_metadata_as_json() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    metadata = {"tags": ["python", "db"]}
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import create_post

        create_post(1, "content", metadata)
    params = cur.execute.call_args[0][1]
    assert params[2] == json.dumps(metadata)


def test_create_post_commits() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import create_post

        create_post(1, "content")
    conn.commit.assert_called_once()


def test_get_post_returns_dict_when_found() -> None:
    from datetime import datetime

    ts = datetime(2024, 1, 1)
    cur = make_cursor(fetchone_val=(1, 2, "Hello", {"tags": []}, ts))
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import get_post

        result = get_post(1)
    assert result is not None
    assert result["content"] == "Hello"


def test_get_post_returns_none_when_not_found() -> None:
    cur = make_cursor(fetchone_val=None)
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import get_post

        result = get_post(999)
    assert result is None


def test_add_comment_returns_new_id() -> None:
    cur = make_cursor(fetchone_val=(5,))
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import add_comment

        result = add_comment(1, 2, "Great post!")
    assert result == 5


def test_add_comment_uses_parameterized_query() -> None:
    cur = make_cursor(fetchone_val=(1,))
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import add_comment

        add_comment(3, 4, "Nice!")
    params = cur.execute.call_args[0][1]
    assert params == (3, 4, "Nice!")


def test_find_posts_by_tag_uses_jsonb_operator() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import find_posts_by_tag

        find_posts_by_tag("python")
    sql = cur.execute.call_args[0][0]
    assert "@>" in sql


def test_find_posts_by_tag_returns_matching_posts() -> None:
    cur = make_cursor(fetchall_val=[(1, 2, "Python post", {"tags": ["python"]})])
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import find_posts_by_tag

        result = find_posts_by_tag("python")
    assert len(result) == 1
    assert result[0]["content"] == "Python post"


def test_find_posts_by_tag_returns_empty_list_when_no_match() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.posts.get_conn", return_value=fake_get_conn(conn)):
        from src.posts import find_posts_by_tag

        result = find_posts_by_tag("nonexistent")
    assert result == []
