-- =========================================================
-- 1. PRODUCT CATEGORY TRANSLATION
-- =========================================================

CREATE TABLE IF NOT EXISTS product_category_name_translation (
    product_category_name VARCHAR(100) NOT NULL,
    product_category_name_english VARCHAR(100) NOT NULL,

    PRIMARY KEY (product_category_name),

    CONSTRAINT uq_category_english
        UNIQUE (product_category_name_english)
);


-- =========================================================
-- 2. CUSTOMERS
-- =========================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(32) NOT NULL,
    customer_unique_id VARCHAR(32) NOT NULL,
    customer_zip_code_prefix VARCHAR(10) NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    customer_state CHAR(2) NOT NULL,

    PRIMARY KEY (customer_id)
);


-- =========================================================
-- 3. ORDERS
-- =========================================================

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(32) NOT NULL,
    customer_id VARCHAR(32) NOT NULL,
    order_status VARCHAR(20) NOT NULL,

    order_purchase_timestamp TIMESTAMP(6) NOT NULL,
    order_approved_at TIMESTAMP(6),
    order_delivered_carrier_date TIMESTAMP(6),
    order_delivered_customer_date TIMESTAMP(6),
    order_estimated_delivery_date TIMESTAMP(6) NOT NULL,

    PRIMARY KEY (order_id),

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- =========================================================
-- 4. PRODUCTS
-- =========================================================

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(32) NOT NULL,
    product_category_name VARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g DECIMAL(12,2),
    product_length_cm DECIMAL(10,2),
    product_height_cm DECIMAL(10,2),
    product_width_cm DECIMAL(10,2),

    PRIMARY KEY (product_id)


);


-- =========================================================
-- 5. SELLERS
-- =========================================================

CREATE TABLE IF NOT EXISTS sellers (
    seller_id VARCHAR(32) NOT NULL,
    seller_zip_code_prefix VARCHAR(10) NOT NULL,
    seller_city VARCHAR(100) NOT NULL,
    seller_state CHAR(2) NOT NULL,

    PRIMARY KEY (seller_id)
);


-- =========================================================
-- 6. ORDER ITEMS
-- =========================================================

CREATE TABLE IF NOT EXISTS order_items (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    shipping_limit_date TIMESTAMP(6) NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    freight_value DECIMAL(12,2) NOT NULL,

    PRIMARY KEY (order_id, order_item_id),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT fk_order_items_seller
        FOREIGN KEY (seller_id)
        REFERENCES sellers(seller_id)
);


-- =========================================================
-- 7. ORDER PAYMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS order_payments (
    order_id VARCHAR(32) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(20) NOT NULL,
    payment_installments INT NOT NULL,
    payment_value DECIMAL(12,2) NOT NULL,

    PRIMARY KEY (order_id, payment_sequential),

    CONSTRAINT fk_order_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);


-- =========================================================
-- 8. ORDER REVIEWS
-- =========================================================

CREATE TABLE IF NOT EXISTS order_reviews (
    review_id VARCHAR(32) NOT NULL,
    order_id VARCHAR(32) NOT NULL,
    review_score INT NOT NULL,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP(6) NOT NULL,
    review_answer_timestamp TIMESTAMP(6) NOT NULL,

    PRIMARY KEY (review_id, order_id),

    CONSTRAINT fk_order_reviews_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);


-- =========================================================
-- 9. GEOLOCATION
-- =========================================================

CREATE TABLE IF NOT EXISTS geolocation (
    geolocation_zip_code_prefix VARCHAR(10) NOT NULL,
    geolocation_lat DECIMAL(10,7) NOT NULL,
    geolocation_lng DECIMAL(10,7) NOT NULL,
    geolocation_city VARCHAR(100) NOT NULL,
    geolocation_state CHAR(2) NOT NULL
);


-- =========================================================
-- INDEXES FOR COMMON JOIN / FILTER COLUMNS
-- =========================================================

CREATE INDEX idx_customers_zip
    ON customers(customer_zip_code_prefix);

CREATE INDEX idx_sellers_zip
    ON sellers(seller_zip_code_prefix);

CREATE INDEX idx_geolocation_zip
    ON geolocation(geolocation_zip_code_prefix);

CREATE INDEX idx_products_category
    ON products(product_category_name);

CREATE INDEX idx_orders_customer
    ON orders(customer_id);

CREATE INDEX idx_order_items_product
    ON order_items(product_id);

CREATE INDEX idx_order_items_seller
    ON order_items(seller_id);

CREATE INDEX idx_payments_order
    ON order_payments(order_id);

CREATE INDEX idx_reviews_order
    ON order_reviews(order_id);