"""Post and comment CRUD operations."""

import json
from typing import Any

from src.db import get_conn


def create_post(user_id: int, content: str, metadata: dict[str, Any] | None = None) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO posts (user_id, content, metadata)
                   VALUES (%s, %s, %s) RETURNING post_id""",
                (user_id, content, json.dumps(metadata or {})),
            )
            row = cur.fetchone()
            conn.commit()
            assert row is not None
            return int(row[0])


def get_post(post_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT post_id, user_id, content, metadata, created_at FROM posts WHERE post_id = %s",
                (post_id,),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return {
        "post_id": row[0],
        "user_id": row[1],
        "content": row[2],
        "metadata": row[3],
        "created_at": row[4],
    }


def add_comment(post_id: int, user_id: int, content: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO comments (post_id, user_id, content)
                   VALUES (%s, %s, %s) RETURNING comment_id""",
                (post_id, user_id, content),
            )
            row = cur.fetchone()
            conn.commit()
            assert row is not None
            return int(row[0])


def find_posts_by_tag(tag: str) -> list[dict[str, Any]]:
    """Use GIN index to find posts containing a specific tag."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT post_id, user_id, content, metadata FROM posts WHERE metadata @> %s",
                (json.dumps({"tags": [tag]}),),
            )
            rows = cur.fetchall()
    return [{"post_id": r[0], "user_id": r[1], "content": r[2], "metadata": r[3]} for r in rows]
