"""Tests for src.feed — get_feed (cache hit/miss), explain_feed_query, invalidate_feed."""

import json
from datetime import datetime
from unittest.mock import patch

from tests.conftest import fake_get_conn, make_conn, make_cursor


def _feed_row() -> tuple:  # type: ignore[type-arg]
    return (1, 2, "alice", "Hello world", {"tags": ["python"]}, datetime(2024, 1, 1))


def test_get_feed_returns_list_on_cache_miss(mock_redis: object) -> None:
    mock_redis.get.return_value = None  # type: ignore[attr-defined]
    cur = make_cursor(fetchall_val=[_feed_row()])
    conn = make_conn(cur)
    with patch("src.feed.get_conn", return_value=fake_get_conn(conn)), patch(
        "src.feed._redis", mock_redis
    ):
        from src.feed import get_feed

        result = get_feed(1)
    assert len(result) == 1
    assert result[0]["username"] == "alice"


def test_get_feed_returns_cached_result_on_hit(mock_redis: object) -> None:
    cached = [{"post_id": 1, "username": "alice", "content": "cached"}]
    mock_redis.get.return_value = json.dumps(cached)  # type: ignore[attr-defined]
    with patch("src.feed._redis", mock_redis):
        from src.feed import get_feed

        result = get_feed(1)
    assert result == cached


def test_get_feed_stores_result_in_redis_on_miss(mock_redis: object) -> None:
    mock_redis.get.return_value = None  # type: ignore[attr-defined]
    cur = make_cursor(fetchall_val=[_feed_row()])
    conn = make_conn(cur)
    with patch("src.feed.get_conn", return_value=fake_get_conn(conn)), patch(
        "src.feed._redis", mock_redis
    ):
        from src.feed import get_feed

        get_feed(1)
    mock_redis.setex.assert_called_once()  # type: ignore[attr-defined]
    key, ttl, _ = mock_redis.setex.call_args[0]  # type: ignore[attr-defined]
    assert "feed:1" in key
    assert ttl == 60


def test_get_feed_uses_row_number_window_function(mock_redis: object) -> None:
    mock_redis.get.return_value = None  # type: ignore[attr-defined]
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.feed.get_conn", return_value=fake_get_conn(conn)), patch(
        "src.feed._redis", mock_redis
    ):
        from src.feed import get_feed

        get_feed(1)
    sql = cur.execute.call_args[0][0]
    assert "ROW_NUMBER()" in sql
    assert "WITH" in sql


def test_get_feed_uses_correct_pagination_params(mock_redis: object) -> None:
    mock_redis.get.return_value = None  # type: ignore[attr-defined]
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.feed.get_conn", return_value=fake_get_conn(conn)), patch(
        "src.feed._redis", mock_redis
    ):
        from src.feed import get_feed

        get_feed(1, page=2, page_size=5)
    params = cur.execute.call_args[0][1]
    # page=2, page_size=5 → rn BETWEEN 6 AND 10
    assert params == (1, 6, 10)


def test_get_feed_returns_empty_list_when_no_posts(mock_redis: object) -> None:
    mock_redis.get.return_value = None  # type: ignore[attr-defined]
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.feed.get_conn", return_value=fake_get_conn(conn)), patch(
        "src.feed._redis", mock_redis
    ):
        from src.feed import get_feed

        result = get_feed(99)
    assert result == []


def test_invalidate_feed_deletes_cache_keys(mock_redis: object) -> None:
    mock_redis.scan_iter.return_value = ["feed:1:page:1", "feed:1:page:2"]  # type: ignore[attr-defined]
    with patch("src.feed._redis", mock_redis):
        from src.feed import invalidate_feed

        invalidate_feed(1)
    assert mock_redis.delete.call_count == 2  # type: ignore[attr-defined]


def test_explain_feed_query_returns_string() -> None:
    cur = make_cursor(fetchall_val=[("Seq Scan on posts",), ("Planning Time: 0.1 ms",)])
    conn = make_conn(cur)
    with patch("src.feed.get_conn", return_value=fake_get_conn(conn)):
        from src.feed import explain_feed_query

        result = explain_feed_query(1)
    assert isinstance(result, str)
    assert "Seq Scan" in result


def test_explain_feed_query_uses_explain_analyze() -> None:
    cur = make_cursor(fetchall_val=[])
    conn = make_conn(cur)
    with patch("src.feed.get_conn", return_value=fake_get_conn(conn)):
        from src.feed import explain_feed_query

        explain_feed_query(1)
    sql = cur.execute.call_args[0][0]
    assert "EXPLAIN ANALYZE" in sql
