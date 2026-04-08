"""Order operations — transactional create + CRUD."""

from typing import Any

from src.db import get_conn


def create_order(customer_id: int, items: list[dict[str, Any]]) -> int:
    """
    Atomically create an order and decrement product stock.

    items: [{"product_id": int, "quantity": int}, ...]
    Raises ValueError if any product has insufficient stock.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1. Lock product rows and validate stock
            product_ids = [i["product_id"] for i in items]
            cur.execute(
                "SELECT product_id, price, stock FROM products WHERE product_id = ANY(%s) FOR UPDATE",
                (product_ids,),
            )
            stock_map = {r[0]: {"price": r[1], "stock": r[2]} for r in cur.fetchall()}

            for item in items:
                pid, qty = item["product_id"], item["quantity"]
                if stock_map[pid]["stock"] < qty:
                    raise ValueError(f"Insufficient stock for product {pid}")

            # 2. Insert order
            cur.execute(
                "INSERT INTO orders (customer_id) VALUES (%s) RETURNING order_id",
                (customer_id,),
            )
            order_id: int = cur.fetchone()[0]  # type: ignore[index]

            # 3. Insert order items + decrement stock
            for item in items:
                pid, qty = item["product_id"], item["quantity"]
                unit_price = stock_map[pid]["price"]
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
                    (order_id, pid, qty, unit_price),
                )
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                    (qty, pid),
                )

        conn.commit()
    return order_id


def get_customer_orders(customer_id: int) -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT o.order_id, o.status, o.created_at,
                          oi.product_id, oi.quantity, oi.unit_price
                   FROM orders o
                   JOIN order_items oi ON oi.order_id = o.order_id
                   WHERE o.customer_id = %s
                   ORDER BY o.created_at DESC""",
                (customer_id,),
            )
            rows = cur.fetchall()

    orders: dict[int, dict[str, Any]] = {}
    for r in rows:
        oid = r[0]
        if oid not in orders:
            orders[oid] = {"order_id": oid, "status": r[1], "created_at": r[2], "items": []}
        orders[oid]["items"].append({"product_id": r[3], "quantity": r[4], "unit_price": float(r[5])})
    return list(orders.values())
