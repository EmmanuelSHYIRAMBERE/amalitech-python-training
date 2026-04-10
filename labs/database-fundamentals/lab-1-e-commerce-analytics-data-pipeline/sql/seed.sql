-- ============================================================
-- Sample seed data
-- ============================================================

INSERT INTO categories (name) VALUES
    ('Electronics'),
    ('Clothing'),
    ('Books')
ON CONFLICT DO NOTHING;

INSERT INTO customers (name, email) VALUES
    ('Alice Martin',  'alice@example.com'),
    ('Bob Nguyen',    'bob@example.com'),
    ('Carol Smith',   'carol@example.com')
ON CONFLICT DO NOTHING;

INSERT INTO products (category_id, name, price, stock, metadata) VALUES
    (1, 'Wireless Headphones', 79.99,  50, '{"color":"black","wireless":true}'),
    (1, 'USB-C Hub',           34.99, 120, '{"ports":7,"color":"silver"}'),
    (1, 'Mechanical Keyboard', 99.99,  30, '{"color":"white","switches":"blue"}'),
    (2, 'Cotton T-Shirt',      19.99, 200, '{"sizes":["S","M","L","XL"],"color":"white"}'),
    (2, 'Running Shoes',       59.99,  80, '{"sizes":["40","41","42","43"],"color":"red"}'),
    (3, 'Clean Code',          39.99,  60, '{"author":"Robert C. Martin","pages":431}'),
    (3, 'The Pragmatic Programmer', 44.99, 45, '{"author":"Hunt & Thomas","pages":352}')
ON CONFLICT DO NOTHING;

-- Orders
INSERT INTO orders (customer_id, status) VALUES
    (1, 'confirmed'),
    (1, 'shipped'),
    (2, 'confirmed'),
    (3, 'pending')
ON CONFLICT DO NOTHING;

-- Order items  (order_id, product_id, quantity, unit_price)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 79.99),
    (1, 6, 2, 39.99),
    (2, 3, 1, 99.99),
    (2, 4, 3, 19.99),
    (3, 2, 2, 34.99),
    (3, 5, 1, 59.99),
    (4, 7, 1, 44.99)
ON CONFLICT DO NOTHING;
