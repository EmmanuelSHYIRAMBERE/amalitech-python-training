"""Customer CRUD operations."""

from typing import Any

from src.db import get_conn


def add_customer(name: str, email: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO customers (name, email) VALUES (%s, %s)
                   ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
                   RETURNING customer_id""",
                (name, email),
            )
            row = cur.fetchone()
            conn.commit()
            return row[0]  # type: ignore[index]


def get_customer(customer_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT customer_id, name, email, created_at FROM customers WHERE customer_id = %s",
                (customer_id,),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return {"customer_id": row[0], "name": row[1], "email": row[2], "created_at": row[3]}
