-- ============================================================
-- E-Commerce Analytics Data Pipeline — DDL (3NF)
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id  SERIAL      PRIMARY KEY,
    name         VARCHAR(120) NOT NULL,
    email        VARCHAR(254) NOT NULL UNIQUE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categories (
    category_id  SERIAL      PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id   SERIAL       PRIMARY KEY,
    category_id  INT          NOT NULL REFERENCES categories(category_id),
    name         VARCHAR(200) NOT NULL,
    price        NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock        INT           NOT NULL DEFAULT 0 CHECK (stock >= 0),
    metadata     JSONB         NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS orders (
    order_id     SERIAL      PRIMARY KEY,
    customer_id  INT         NOT NULL REFERENCES customers(customer_id),
    status       VARCHAR(20) NOT NULL DEFAULT 'pending'
                             CHECK (status IN ('pending','confirmed','shipped','cancelled')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL        PRIMARY KEY,
    order_id      INT           NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id    INT           NOT NULL REFERENCES products(product_id),
    quantity      INT           NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0)
);

-- ── Indexes ──────────────────────────────────────────────────
-- B-tree: fast lookup of orders by customer
CREATE INDEX IF NOT EXISTS idx_orders_customer_id
    ON orders(customer_id);

-- GIN: efficient JSONB attribute queries on products
CREATE INDEX IF NOT EXISTS idx_products_metadata
    ON products USING GIN (metadata);
