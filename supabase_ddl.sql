-- ============================================================
-- DDL Script untuk Supabase - E-Commerce Database
-- Sesuai dengan ERD yang telah dirancang
-- ============================================================

-- ============================================================
-- 1. DROP TABLES (jika sudah ada) - urutan sesuai dependency
-- ============================================================
DROP TABLE IF EXISTS stock CASCADE;

DROP TABLE IF EXISTS product_review CASCADE;

DROP TABLE IF EXISTS order_items CASCADE;

DROP TABLE IF EXISTS "order" CASCADE;

DROP TABLE IF EXISTS shipping CASCADE;

DROP TABLE IF EXISTS customer_address CASCADE;

DROP TABLE IF EXISTS product CASCADE;

DROP TABLE IF EXISTS store CASCADE;

DROP TABLE IF EXISTS category CASCADE;

DROP TABLE IF EXISTS brand CASCADE;

DROP TABLE IF EXISTS customer CASCADE;

DROP TABLE IF EXISTS country CASCADE;

-- ============================================================
-- 2. CREATE TABLES - Master Data (tanpa FK dulu)
-- ============================================================

-- Tabel Country
CREATE TABLE country (
    country_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Tabel Store
CREATE TABLE store (
    store_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Tabel Category
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Tabel Brand
CREATE TABLE brand (
    brand_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- ============================================================
-- 3. CREATE TABLES - dengan Foreign Key
-- ============================================================

-- Tabel Customer (FK: country_id)
CREATE TABLE customer (
    customer_id INT PRIMARY KEY,
    country_id INT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    gender VARCHAR(20),
    signup_date DATE,
    CONSTRAINT fk_customer_country FOREIGN KEY (country_id) REFERENCES country (country_id)
);

-- Tabel Customer_Address (FK: customer_id)
CREATE TABLE customer_address (
    customer_address_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    address VARCHAR(255),
    CONSTRAINT fk_address_customer FOREIGN KEY (customer_id) REFERENCES customer (customer_id)
);

-- Tabel Shipping (FK: customer_address_id)
CREATE TABLE shipping (
    shipping_id SERIAL PRIMARY KEY,
    customer_address_id INT,
    shipping_status VARCHAR(50),
    shipping_cost DECIMAL(10, 2),
    CONSTRAINT fk_shipping_address FOREIGN KEY (customer_address_id) REFERENCES customer_address (customer_address_id)
);

-- Tabel Product (FK: store_id, category_id, brand_id)
CREATE TABLE product (
    product_id INT PRIMARY KEY,
    store_id INT,
    category_id INT,
    brand_id INT,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2),
    stock_quantity INT DEFAULT 0,
    CONSTRAINT fk_product_store FOREIGN KEY (store_id) REFERENCES store (store_id),
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES category (category_id),
    CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) REFERENCES brand (brand_id)
);

-- Tabel Order (FK: customer_id, shipping_id)
CREATE TABLE "order" (
    order_id INT PRIMARY KEY,
    customer_id INT,
    shipping_id INT,
    order_date DATE,
    payment_method VARCHAR(50),
    total_amount DECIMAL(12, 2),
    order_status VARCHAR(50),
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
    CONSTRAINT fk_order_shipping FOREIGN KEY (shipping_id) REFERENCES shipping (shipping_id)
);

-- Tabel Order_Items (FK: product_id, order_id)
CREATE TABLE order_items (
    order_items_id INT PRIMARY KEY,
    product_id INT,
    order_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    CONSTRAINT fk_orderitems_product FOREIGN KEY (product_id) REFERENCES product (product_id),
    CONSTRAINT fk_orderitems_order FOREIGN KEY (order_id) REFERENCES "order" (order_id)
);

-- Tabel Product_Review (FK: product_id, customer_id)
CREATE TABLE product_review (
    review_id INT PRIMARY KEY,
    product_id INT,
    customer_id INT,
    rating INT CHECK (
        rating >= 1
        AND rating <= 5
    ),
    review_text TEXT,
    review_date DATE,
    CONSTRAINT fk_review_product FOREIGN KEY (product_id) REFERENCES product (product_id),
    CONSTRAINT fk_review_customer FOREIGN KEY (customer_id) REFERENCES customer (customer_id)
);

-- Tabel Stock (FK: product_id)
CREATE TABLE stock (
    stock_id SERIAL PRIMARY KEY,
    product_id INT,
    quantity_change INT,
    movement_type VARCHAR(20),
    change_date DATE,
    CONSTRAINT fk_stock_product FOREIGN KEY (product_id) REFERENCES product (product_id)
);

-- ============================================================
-- 4. CREATE INDEXES untuk optimasi query
-- ============================================================

-- Index untuk Foreign Keys
CREATE INDEX idx_customer_country ON customer (country_id);

CREATE INDEX idx_address_customer ON customer_address (customer_id);

CREATE INDEX idx_shipping_address ON shipping (customer_address_id);

CREATE INDEX idx_product_store ON product (store_id);

CREATE INDEX idx_product_category ON product (category_id);

CREATE INDEX idx_product_brand ON product (brand_id);

CREATE INDEX idx_order_customer ON "order" (customer_id);

CREATE INDEX idx_order_shipping ON "order" (shipping_id);

CREATE INDEX idx_orderitems_product ON order_items (product_id);

CREATE INDEX idx_orderitems_order ON order_items (order_id);

CREATE INDEX idx_review_product ON product_review (product_id);

CREATE INDEX idx_review_customer ON product_review (customer_id);

CREATE INDEX idx_stock_product ON stock (product_id);

-- Index untuk kolom yang sering di-query
CREATE INDEX idx_customer_email ON customer (email);

CREATE INDEX idx_order_date ON "order" (order_date);

CREATE INDEX idx_order_status ON "order" (order_status);

CREATE INDEX idx_product_name ON product (name);

CREATE INDEX idx_review_rating ON product_review (rating);

CREATE INDEX idx_stock_date ON stock (change_date);

-- ============================================================
-- CATATAN IMPORT CSV ke Supabase:
-- ============================================================
-- Urutan import CSV (sesuai dependency):
-- 1. country.csv
-- 2. store.csv
-- 3. category.csv
-- 4. brand.csv
-- 5. customer.csv
-- 6. customer_address.csv
-- 7. shipping.csv
-- 8. product.csv
-- 9. order.csv
-- 10. order_items.csv
-- 11. product_review.csv
-- 12. stock.csv
-- ============================================================