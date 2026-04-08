# Lab 1 — E-Commerce Analytics Data Pipeline

## ER Diagram

```
┌──────────────┐        ┌──────────────────┐        ┌───────────────┐
│  customers   │        │     orders       │        │  order_items  │
│──────────────│1      *│──────────────────│1      *│───────────────│
│ customer_id  │────────│ order_id         │────────│ order_item_id │
│ name         │        │ customer_id (FK) │        │ order_id (FK) │
│ email        │        │ status           │        │ product_id(FK)│
│ created_at   │        │ created_at       │        │ quantity      │
└──────────────┘        └──────────────────┘        │ unit_price    │
                                                     └───────┬───────┘
                                                             │*
                                                             │
                                                      1┌─────┴──────┐
                                                       │  products  │
                                                       │────────────│
                                                       │ product_id │
                                                       │category_id │──────┐
                                                       │ name       │      │1
                                                       │ price      │ ┌────┴──────────┐
                                                       │ stock      │ │  categories   │
                                                       │ metadata   │ │───────────────│
                                                       │  (JSONB)   │ │ category_id   │
                                                       └────────────┘ │ name          │
                                                                      └───────────────┘
```

## Schema Design & Normalization (3NF)

| Decision | Rationale |
|---|---|
| `categories` is a separate table | Eliminates repeating category strings in `products` (2NF → 3NF) |
| `unit_price` stored in `order_items` | Price at time of purchase is independent of current `products.price` |
| `order_items` junction table | Resolves the many-to-many between orders and products |
| `metadata JSONB` on `products` | Flexible per-category attributes (sizes, colors) without nullable columns |
| All FK constraints declared | Referential integrity enforced at the DB level |
| `CHECK` constraints on price/stock/status | Domain integrity without application-layer guards |

## NoSQL Integration

| Store | Purpose |
|---|---|
| **Redis** | Cache top-10 best-sellers query result (TTL 300 s). Avoids repeated aggregation on every page load. Cache is invalidated on `add_product`. |
| **MongoDB** | Store unstructured shopping-cart sessions before checkout. Schema-free documents suit the variable cart contents per user. |

## Project Structure

```
lab-1-e-commerce-analytics-data-pipeline/
├── docker-compose.yml      # PostgreSQL 16, Redis 7, MongoDB 7
├── sql/
│   ├── schema.sql          # DDL — tables, constraints, indexes
│   └── seed.sql            # Sample data
├── src/
│   ├── db.py               # psycopg2 ThreadedConnectionPool
│   ├── customers.py        # Customer CRUD
│   ├── products.py         # Product CRUD + Redis cache
│   ├── orders.py           # Transactional order creation
│   ├── sessions.py         # MongoDB cart sessions
│   └── analytics.py        # Window functions, CTEs, EXPLAIN ANALYZE
├── main.py                 # Full pipeline demo
├── requirements.txt
└── pyproject.toml
```

## Running the Pipeline

```bash
# 1. Start all services
docker compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the demo
python main.py
```

## Query Optimization Report

### Query: Find all orders for a customer

```sql
SELECT * FROM orders WHERE customer_id = 1;
```

#### Before index — EXPLAIN ANALYZE output (Seq Scan)

```
Seq Scan on orders  (cost=0.00..1.04 rows=1 width=28)
                    (actual time=0.012..0.015 rows=2 loops=1)
  Filter: (customer_id = 1)
  Rows Removed by Filter: 2
Planning Time: 0.08 ms
Execution Time: 0.03 ms
```

The planner performs a **sequential scan** over the entire `orders` table, examining every row.

#### After B-tree index

```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

```
Index Scan using idx_orders_customer_id on orders
                    (cost=0.14..8.16 rows=1 width=28)
                    (actual time=0.018..0.021 rows=2 loops=1)
  Index Cond: (customer_id = 1)
Planning Time: 0.15 ms
Execution Time: 0.04 ms
```

The planner switches to an **Index Scan**, directly locating matching rows. At scale (millions of orders) this reduces I/O from O(n) to O(log n).

### Query: Find products by JSONB attribute

```sql
SELECT * FROM products WHERE metadata @> '{"wireless": true}';
```

#### Before GIN index — Seq Scan

```
Seq Scan on products  (cost=0.00..1.09 rows=1 width=...)
  Filter: (metadata @> '{"wireless": true}'::jsonb)
```

#### After GIN index

```sql
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);
```

```
Bitmap Heap Scan on products  (cost=4.01..8.03 rows=1 width=...)
  Recheck Cond: (metadata @> '{"wireless": true}'::jsonb)
  ->  Bitmap Index Scan on idx_products_metadata
```

The GIN index enables **Bitmap Index Scan** on the JSONB column, avoiding a full table scan for attribute lookups.

---

*Python 3.11+ · PostgreSQL 16 · Redis 7 · MongoDB 7 · AmaliTech Training Program*
