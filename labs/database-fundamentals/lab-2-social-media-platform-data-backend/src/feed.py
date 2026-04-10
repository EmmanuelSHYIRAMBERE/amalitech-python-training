"""Feed generation — CTE, ROW_NUMBER() pagination, Redis cache, EXPLAIN ANALYZE."""

import json
import logging
import os
from typing import Any

import redis

from src.db import get_conn

log = logging.getLogger(__name__)

_redis = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://127.0.0.1:6380/0"), decode_responses=True
)
_FEED_TTL = 60  # seconds


def _feed_key(user_id: int, page: int) -> str:
    return f"feed:{user_id}:page:{page}"


# ── Feed query: CTE + ROW_NUMBER() window function ────────────────────────────
_FEED_SQL = """
WITH followed_posts AS (
    SELECT
        p.post_id,
        p.user_id,
        u.username,
        p.content,
        p.metadata,
        p.created_at,
        ROW_NUMBER() OVER (ORDER BY p.created_at DESC) AS rn
    FROM posts p
    JOIN users u ON u.user_id = p.user_id
    WHERE p.user_id IN (
        SELECT following_id FROM followers WHERE follower_id = %s
    )
)
SELECT post_id, user_id, username, content, metadata, created_at
FROM followed_posts
WHERE rn BETWEEN %s AND %s
ORDER BY created_at DESC;
"""


def get_feed(user_id: int, page: int = 1, page_size: int = 10) -> list[dict[str, Any]]:
    """Return paginated timeline for user_id; result is Redis-cached."""
    key = _feed_key(user_id, page)
    cached = _redis.get(key)
    if cached:
        log.info("Feed cache HIT — user=%d page=%d", user_id, page)
        return json.loads(cached)  # type: ignore[no-any-return, arg-type]

    log.info("Feed cache MISS — querying database user=%d page=%d", user_id, page)
    offset_start = (page - 1) * page_size + 1
    offset_end = page * page_size

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_FEED_SQL, (user_id, offset_start, offset_end))
            rows = cur.fetchall()

    result: list[dict[str, Any]] = [
        {
            "post_id": r[0],
            "user_id": r[1],
            "username": r[2],
            "content": r[3],
            "metadata": r[4],
            "created_at": r[5].isoformat(),
        }
        for r in rows
    ]
    _redis.setex(key, _FEED_TTL, json.dumps(result))
    return result


def invalidate_feed(user_id: int) -> None:
    """Remove all cached feed pages for a user."""
    for key in _redis.scan_iter(f"feed:{user_id}:page:*"):
        _redis.delete(key)


def explain_feed_query(user_id: int) -> str:
    """Run EXPLAIN ANALYZE on the feed query and return the plan as text."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"EXPLAIN ANALYZE {_FEED_SQL}",
                (user_id, 1, 10),
            )
            lines = [row[0] for row in cur.fetchall()]
    return "\n".join(lines)
