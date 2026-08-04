"""Complex analytical queries — window functions, CTEs, EXPLAIN ANALYZE."""

from typing import Any

from src.db import get_conn

# ── Window function: rank products by sales within each category ──────────────
_RANK_SQL = """
SELECT
    c.name          AS category,
    p.name          AS product,
    SUM(oi.quantity) AS units_sold,
    RANK() OVER (
        PARTITION BY p.category_id
        ORDER BY SUM(oi.quantity) DESC
    ) AS sales_rank
FROM order_items oi
JOIN products  p ON p.product_id  = oi.product_id
JOIN categories c ON c.category_id = p.category_id
GROUP BY p.category_id, p.product_id, c.name, p.name
ORDER BY c.name, sales_rank;
"""

# ── CTE: total revenue per customer ──────────────────────────────────────────
_REVENUE_SQL = """
WITH order_totals AS (
    SELECT o.customer_id,
           SUM(oi.quantity * oi.unit_price) AS order_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id, o.customer_id
)
SELECT cu.customer_id, cu.name, SUM(ot.order_revenue) AS total_revenue
FROM order_totals ot
JOIN customers cu ON cu.customer_id = ot.customer_id
GROUP BY cu.customer_id, cu.name
ORDER BY total_revenue DESC;
"""


def rank_products_by_category() -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_RANK_SQL)
            rows = cur.fetchall()
    return [{"category": r[0], "product": r[1], "units_sold": r[2], "rank": r[3]} for r in rows]


def revenue_per_customer() -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_REVENUE_SQL)
            rows = cur.fetchall()
    return [{"customer_id": r[0], "name": r[1], "total_revenue": float(r[2])} for r in rows]


def explain_customer_orders(customer_id: int) -> str:
    """Run EXPLAIN ANALYZE for get_customer_orders and return the plan as text."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = %s",
                (customer_id,),
            )
            lines = [row[0] for row in cur.fetchall()]
    return "\n".join(lines)
