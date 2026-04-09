"""Product CRUD + Redis cache for top-10 best-sellers."""

import json
import logging
import os
from typing import Any

import redis

from src.db import get_conn

log = logging.getLogger(__name__)
_redis = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True
)
_TOP10_KEY = "top10_products"
_TOP10_TTL = 300  # seconds


def add_product(
    category_id: int, name: str, price: float, stock: int, metadata: dict[str, Any]
) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO products (category_id, name, price, stock, metadata)
                   VALUES (%s, %s, %s, %s, %s) RETURNING product_id""",
                (category_id, name, price, stock, json.dumps(metadata)),
            )
            row = cur.fetchone()
            conn.commit()
            _redis.delete(_TOP10_KEY)  # invalidate cache
            assert row is not None
            return int(row[0])


def get_product(product_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT product_id, category_id, name, price, stock, metadata FROM products WHERE product_id = %s",
                (product_id,),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return {
        "product_id": row[0],
        "category_id": row[1],
        "name": row[2],
        "price": float(row[3]),
        "stock": row[4],
        "metadata": row[5],
    }


def get_top10_best_sellers() -> list[dict[str, Any]]:
    """Return top-10 products by units sold; result is Redis-cached."""
    cached = _redis.get(_TOP10_KEY)
    if cached:
        log.info("Cache HIT — returning top-10 from Redis (no DB query)")
        return json.loads(cached)  # type: ignore[arg-type, no-any-return]

    log.info("Cache MISS — querying database and caching result")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT p.product_id, p.name, SUM(oi.quantity) AS units_sold
                   FROM order_items oi
                   JOIN products p ON p.product_id = oi.product_id
                   GROUP BY p.product_id, p.name
                   ORDER BY units_sold DESC
                   LIMIT 10""")
            rows = cur.fetchall()

    result: list[dict[str, Any]] = [{"product_id": r[0], "name": r[1], "units_sold": r[2]} for r in rows]
    _redis.setex(_TOP10_KEY, _TOP10_TTL, json.dumps(result))
    return result


def find_products_by_metadata(key: str, value: Any) -> list[dict[str, Any]]:
    """Use GIN index to find products where metadata->key = value."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT product_id, name, metadata FROM products WHERE metadata @> %s",
                (json.dumps({key: value}),),
            )
            rows = cur.fetchall()
    return [{"product_id": r[0], "name": r[1], "metadata": r[2]} for r in rows]
