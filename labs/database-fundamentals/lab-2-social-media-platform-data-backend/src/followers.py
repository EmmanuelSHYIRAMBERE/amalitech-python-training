"""Follower relationship operations — transactional follow/unfollow."""

from typing import Any

from src.db import get_conn


def follow_user(follower_id: int, following_id: int) -> None:
    """
    Atomically record that follower_id follows following_id.
    Raises ValueError if a user tries to follow themselves.
    """
    if follower_id == following_id:
        raise ValueError("A user cannot follow themselves.")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO followers (follower_id, following_id)
                   VALUES (%s, %s) ON CONFLICT DO NOTHING""",
                (follower_id, following_id),
            )
        conn.commit()


def unfollow_user(follower_id: int, following_id: int) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM followers WHERE follower_id = %s AND following_id = %s",
                (follower_id, following_id),
            )
        conn.commit()


def get_following(user_id: int) -> list[dict[str, Any]]:
    """Return list of users that user_id follows."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT u.user_id, u.username
                   FROM followers f
                   JOIN users u ON u.user_id = f.following_id
                   WHERE f.follower_id = %s""",
                (user_id,),
            )
            rows = cur.fetchall()
    return [{"user_id": r[0], "username": r[1]} for r in rows]


def get_followers(user_id: int) -> list[dict[str, Any]]:
    """Return list of users that follow user_id."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT u.user_id, u.username
                   FROM followers f
                   JOIN users u ON u.user_id = f.follower_id
                   WHERE f.following_id = %s""",
                (user_id,),
            )
            rows = cur.fetchall()
    return [{"user_id": r[0], "username": r[1]} for r in rows]
