"""User CRUD operations."""

from typing import Any

from src.db import get_conn


def create_user(username: str, email: str, bio: str = "") -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO users (username, email, bio) VALUES (%s, %s, %s)
                   ON CONFLICT (email) DO UPDATE SET username = EXCLUDED.username
                   RETURNING user_id""",
                (username, email, bio),
            )
            row = cur.fetchone()
            conn.commit()
            assert row is not None
            return int(row[0])


def get_user(user_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, username, email, bio, created_at FROM users WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return {
        "user_id": row[0],
        "username": row[1],
        "email": row[2],
        "bio": row[3],
        "created_at": row[4],
    }
