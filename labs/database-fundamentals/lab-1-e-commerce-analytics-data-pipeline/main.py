"""CLI entry point — demonstrates the full e-commerce analytics pipeline."""

import logging
import uuid

from src.analytics import explain_customer_orders, rank_products_by_category, revenue_per_customer
from src.customers import add_customer, get_customer
from src.orders import create_order, get_customer_orders
from src.products import add_product, find_products_by_metadata, get_top10_best_sellers
from src.sessions import delete_cart, get_cart, save_cart

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    # ── 1. Customer ───────────────────────────────────────────────────────────
    log.info("=== Customer ===")
    cid = add_customer("Diana Prince", "diana@example.com")
    log.info("Created customer id=%d  →  %s", cid, get_customer(cid))

    # ── 2. Product with JSONB metadata ────────────────────────────────────────
    log.info("=== Product ===")
    pid = add_product(1, "Smart Watch", 149.99, 25, {"color": "black", "wireless": True})
    log.info("Created product id=%d", pid)

    # ── 3. MongoDB cart session ───────────────────────────────────────────────
    log.info("=== Cart Session (MongoDB) ===")
    session_id = str(uuid.uuid4())
    save_cart(session_id, cid, [{"product_id": pid, "quantity": 1}])
    cart = get_cart(session_id)
    log.info("Cart: %s", cart)

    # ── 4. Transactional order creation ──────────────────────────────────────
    log.info("=== Create Order (ACID transaction) ===")
    order_id = create_order(cid, [{"product_id": pid, "quantity": 1}])
    log.info("Order created id=%d", order_id)
    delete_cart(session_id)  # clear cart after checkout

    # ── 5. Redis-cached top-10 best sellers ──────────────────────────────────
    log.info("=== Top-10 Best Sellers (Redis cache) ===")
    for p in get_top10_best_sellers():
        log.info("  %s — %d units", p["name"], p["units_sold"])

    # ── 6. JSONB metadata query (GIN index) ───────────────────────────────────
    log.info("=== JSONB Query: wireless products ===")
    for p in find_products_by_metadata("wireless", True):
        log.info("  %s  %s", p["name"], p["metadata"])

    # ── 7. Customer orders ────────────────────────────────────────────────────
    log.info("=== Customer Orders ===")
    for o in get_customer_orders(cid):
        log.info("  order=%d status=%s items=%d", o["order_id"], o["status"], len(o["items"]))

    # ── 8. Analytics: window function ─────────────────────────────────────────
    log.info("=== Product Rank by Category (RANK window function) ===")
    for r in rank_products_by_category():
        log.info("  [%s] rank=%d  %s  (%d sold)", r["category"], r["rank"], r["product"], r["units_sold"])

    # ── 9. Analytics: CTE revenue ─────────────────────────────────────────────
    log.info("=== Revenue per Customer (CTE) ===")
    for r in revenue_per_customer():
        log.info("  %s → $%.2f", r["name"], r["total_revenue"])

    # ── 10. EXPLAIN ANALYZE ───────────────────────────────────────────────────
    log.info("=== EXPLAIN ANALYZE: orders by customer_id ===")
    print(explain_customer_orders(cid))


if __name__ == "__main__":
    main()
