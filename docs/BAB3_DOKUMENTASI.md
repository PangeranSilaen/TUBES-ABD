# BAB III - IMPLEMENTASI DAN ANALISIS

## 3.1. Implementasi Database

### 3.1.1. Platform Database

Implementasi basis data pada penelitian ini menggunakan **Supabase** sebagai *Database as a Service* (DBaaS) yang berbasis PostgreSQL. Supabase dipilih karena menyediakan layanan database relasional yang handal dengan fitur-fitur modern seperti:

- PostgreSQL sebagai engine database yang mendukung SQL standar
- REST API otomatis untuk akses data
- Realtime subscriptions untuk update data secara langsung
- Row Level Security (RLS) untuk keamanan data
- Dashboard web untuk manajemen database

**Informasi Koneksi Database:**
- **Host:** db.lokizaoluolkdetelmfd.supabase.co
- **Database Engine:** PostgreSQL 17.6.1
- **Region:** Southeast Asia (Singapore)

### 3.1.2. Data Definition Language (DDL)

Berikut adalah script DDL yang digunakan untuk membuat struktur tabel dalam basis data:

```sql
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
    CONSTRAINT fk_customer_country 
        FOREIGN KEY (country_id) REFERENCES country(country_id)
);

-- Tabel Customer_Address (FK: customer_id)
CREATE TABLE customer_address (
    customer_address_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    address VARCHAR(255),
    CONSTRAINT fk_address_customer 
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

-- Tabel Shipping (FK: customer_address_id)
CREATE TABLE shipping (
    shipping_id SERIAL PRIMARY KEY,
    customer_address_id INT,
    shipping_status VARCHAR(50),
    shipping_cost DECIMAL(10, 2),
    CONSTRAINT fk_shipping_address 
        FOREIGN KEY (customer_address_id) REFERENCES customer_address(customer_address_id)
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
    CONSTRAINT fk_product_store 
        FOREIGN KEY (store_id) REFERENCES store(store_id),
    CONSTRAINT fk_product_category 
        FOREIGN KEY (category_id) REFERENCES category(category_id),
    CONSTRAINT fk_product_brand 
        FOREIGN KEY (brand_id) REFERENCES brand(brand_id)
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
    CONSTRAINT fk_order_customer 
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT fk_order_shipping 
        FOREIGN KEY (shipping_id) REFERENCES shipping(shipping_id)
);

-- Tabel Order_Items (FK: product_id, order_id)
CREATE TABLE order_items (
    order_items_id INT PRIMARY KEY,
    product_id INT,
    order_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    CONSTRAINT fk_orderitems_product 
        FOREIGN KEY (product_id) REFERENCES product(product_id),
    CONSTRAINT fk_orderitems_order 
        FOREIGN KEY (order_id) REFERENCES "order"(order_id)
);

-- Tabel Product_Review (FK: product_id, customer_id)
CREATE TABLE product_review (
    review_id INT PRIMARY KEY,
    product_id INT,
    customer_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATE,
    CONSTRAINT fk_review_product 
        FOREIGN KEY (product_id) REFERENCES product(product_id),
    CONSTRAINT fk_review_customer 
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

-- Tabel Stock (FK: product_id)
CREATE TABLE stock (
    stock_id SERIAL PRIMARY KEY,
    product_id INT,
    quantity_change INT,
    movement_type VARCHAR(20),
    change_date DATE,
    CONSTRAINT fk_stock_product 
        FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- ============================================================
-- 4. CREATE INDEXES untuk optimasi query
-- ============================================================

-- Index untuk Foreign Keys
CREATE INDEX idx_customer_country ON customer(country_id);
CREATE INDEX idx_address_customer ON customer_address(customer_id);
CREATE INDEX idx_shipping_address ON shipping(customer_address_id);
CREATE INDEX idx_product_store ON product(store_id);
CREATE INDEX idx_product_category ON product(category_id);
CREATE INDEX idx_product_brand ON product(brand_id);
CREATE INDEX idx_order_customer ON "order"(customer_id);
CREATE INDEX idx_order_shipping ON "order"(shipping_id);
CREATE INDEX idx_orderitems_product ON order_items(product_id);
CREATE INDEX idx_orderitems_order ON order_items(order_id);
CREATE INDEX idx_review_product ON product_review(product_id);
CREATE INDEX idx_review_customer ON product_review(customer_id);
CREATE INDEX idx_stock_product ON stock(product_id);

-- Index untuk kolom yang sering di-query
CREATE INDEX idx_customer_email ON customer(email);
CREATE INDEX idx_order_date ON "order"(order_date);
CREATE INDEX idx_order_status ON "order"(order_status);
CREATE INDEX idx_product_name ON product(name);
CREATE INDEX idx_review_rating ON product_review(rating);
CREATE INDEX idx_stock_date ON stock(change_date);
```

### 3.1.3. Struktur Tabel Database

Berikut adalah ringkasan struktur tabel yang telah diimplementasikan:

| No | Nama Tabel | Jumlah Record | Keterangan |
|----|------------|---------------|------------|
| 1 | country | 243 | Data negara pelanggan |
| 2 | store | 10 | Data toko/penjual |
| 3 | category | 6 | Kategori produk |
| 4 | brand | 4 | Merek produk |
| 5 | customer | 5,000 | Data pelanggan |
| 6 | customer_address | 6,705 | Alamat pelanggan |
| 7 | shipping | 20,117 | Data pengiriman |
| 8 | product | 18,356 | Data produk |
| 9 | order | 20,117 | Transaksi pesanan |
| 10 | order_items | 50,233 | Item dalam pesanan |
| 11 | product_review | 9,221 | Ulasan produk |
| 12 | stock | 16,610 | Pergerakan stok |

---

## 3.2. Pembersihan / Preprocessing Data

### 3.2.1. Transformasi Data

Dataset awal yang diperoleh dari Kaggle memiliki struktur sederhana dengan 5 tabel. Untuk memenuhi kebutuhan normalisasi dan perancangan ERD yang lebih kompleks, dilakukan transformasi data menggunakan script Python.

**Script Preprocessing (generate_new_tables.py):**

```python
"""
Script untuk Generate Tabel-Tabel Baru sesuai ERD
==================================================
Script ini akan:
1. Membaca CSV existing dari folder /resized
2. Extract data untuk tabel lookup (country, category, brand, store)
3. Generate data dummy untuk tabel baru (customer_address, shipping, stock)
4. Memodifikasi tabel existing untuk menambah FK
5. Menyimpan semua CSV baru ke folder /resized_new
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

# Set random seed untuk reproducibility
random.seed(42)
np.random.seed(42)

# Path konfigurasi
BASE_PATH = "path/to/project"
INPUT_PATH = os.path.join(BASE_PATH, "resized")
OUTPUT_PATH = os.path.join(BASE_PATH, "resized_new")

# Buat folder output jika belum ada
os.makedirs(OUTPUT_PATH, exist_ok=True)
```

### 3.2.2. Proses Transformasi

Berikut adalah proses transformasi yang dilakukan:

1. **Ekstraksi Tabel Lookup**
   - `country`: Diekstrak dari kolom `country` pada tabel customers
   - `category`: Diekstrak dari kolom `category` pada tabel products
   - `brand`: Diekstrak dari kolom `brand` pada tabel products

2. **Generate Data Dummy**
   - `store`: 10 toko dengan nama dummy
   - `customer_address`: Alamat untuk pelanggan dengan template Indonesia dan Internasional
   - `shipping`: Data pengiriman dengan status (Pending, Processing, Shipped, In Transit, Delivered, Cancelled)
   - `stock`: Riwayat pergerakan stok (IN, OUT, ADJUSTMENT)

3. **Modifikasi Tabel Existing**
   - `customer`: Ditambahkan `country_id` sebagai Foreign Key
   - `product`: Ditambahkan `store_id`, `category_id`, `brand_id` sebagai Foreign Key
   - `order`: Ditambahkan `shipping_id` dan `order_status`

### 3.2.3. Hasil Transformasi

| Tabel Asal | Transformasi | Tabel Hasil |
|------------|--------------|-------------|
| customers.csv | Extract country → Tabel baru | country.csv |
| customers.csv | Tambah country_id FK | customer.csv |
| - | Generate dummy | customer_address.csv |
| - | Generate dummy | shipping.csv |
| products.csv | Extract category → Tabel baru | category.csv |
| products.csv | Extract brand → Tabel baru | brand.csv |
| - | Generate dummy | store.csv |
| products.csv | Tambah store_id, category_id, brand_id FK | product.csv |
| orders.csv | Tambah shipping_id, order_status | order.csv |
| order_items.csv | Rename column | order_items.csv |
| product_reviews.csv | No change | product_review.csv |
| - | Generate dummy | stock.csv |

---

## 3.3. Hasil Analisis

### 3.3.1. Data Manipulation Language (DML) - Query Analisis

Berikut adalah query SQL yang digunakan untuk menganalisis data dalam dashboard:

#### A. Query Overview Dashboard

```sql
-- Total Customers
SELECT COUNT(*) AS total_customers FROM customer;

-- Total Orders dan Revenue
SELECT COUNT(*) AS total_orders, 
       SUM(total_amount) AS total_revenue 
FROM "order";

-- Total Products
SELECT COUNT(*) AS total_products FROM product;

-- Average Rating
SELECT AVG(rating) AS avg_rating FROM product_review;

-- Orders Trend (Monthly)
SELECT DATE_TRUNC('month', order_date) as month, 
       COUNT(*) AS total_orders,
       SUM(total_amount) AS revenue
FROM "order"
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Payment Method Distribution
SELECT payment_method, COUNT(*) as count
FROM "order"
GROUP BY payment_method;

-- Top Categories by Revenue
SELECT c.name as category, 
       SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN product p ON oi.product_id = p.product_id
JOIN category c ON p.category_id = c.category_id
GROUP BY c.name
ORDER BY revenue DESC
LIMIT 10;

-- Top Brands by Revenue
SELECT b.name as brand, 
       SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN product p ON oi.product_id = p.product_id
JOIN brand b ON p.brand_id = b.brand_id
GROUP BY b.name
ORDER BY revenue DESC
LIMIT 10;
```

#### B. Query Customer Analytics

```sql
-- Top Countries by Customers
SELECT co.name as country, COUNT(c.customer_id) as total_customers
FROM customer c
JOIN country co ON c.country_id = co.country_id
GROUP BY co.name
ORDER BY total_customers DESC
LIMIT 15;

-- Gender Distribution
SELECT gender, COUNT(*) as count
FROM customer
WHERE gender IS NOT NULL
GROUP BY gender;

-- Customer Signups Over Time
SELECT DATE_TRUNC('month', signup_date) as month, COUNT(*) as signups
FROM customer
WHERE signup_date IS NOT NULL
GROUP BY DATE_TRUNC('month', signup_date)
ORDER BY month;

-- Top Customers by Spending
SELECT c.customer_id, c.name, c.email, co.name as country,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as total_spent
FROM customer c
JOIN "order" o ON c.customer_id = o.customer_id
JOIN country co ON c.country_id = co.country_id
GROUP BY c.customer_id, c.name, c.email, co.name
ORDER BY total_spent DESC
LIMIT 10;
```

#### C. Query Product Analytics

```sql
-- Products per Category
SELECT c.name as category, COUNT(p.product_id) as product_count
FROM product p
JOIN category c ON p.category_id = c.category_id
GROUP BY c.name
ORDER BY product_count DESC;

-- Products per Brand
SELECT b.name as brand, COUNT(p.product_id) as product_count
FROM product p
JOIN brand b ON p.brand_id = b.brand_id
GROUP BY b.name
ORDER BY product_count DESC;

-- Products per Store
SELECT s.name as store, COUNT(p.product_id) as product_count,
       AVG(p.price) as avg_price
FROM product p
JOIN store s ON p.store_id = s.store_id
GROUP BY s.name
ORDER BY product_count DESC;

-- Best Selling Products (JOIN 5 tabel)
SELECT p.product_id, p.name, c.name as category, b.name as brand,
       s.name as store, p.price,
       SUM(oi.quantity) as total_sold,
       SUM(oi.quantity * oi.unit_price) as revenue
FROM product p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN category c ON p.category_id = c.category_id
JOIN brand b ON p.brand_id = b.brand_id
JOIN store s ON p.store_id = s.store_id
GROUP BY p.product_id, p.name, c.name, b.name, s.name, p.price
ORDER BY total_sold DESC
LIMIT 10;
```

#### D. Query Order Analytics

```sql
-- Order Status Distribution
SELECT order_status, COUNT(*) as count
FROM "order"
GROUP BY order_status;

-- Revenue by Payment Method
SELECT payment_method, SUM(total_amount) as revenue
FROM "order"
GROUP BY payment_method;

-- Monthly Revenue Trend
SELECT DATE_TRUNC('month', order_date) as month,
       COUNT(*) as orders,
       SUM(total_amount) as revenue
FROM "order"
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Recent Orders with Customer Info
SELECT o.order_id, c.name as customer, o.order_date, 
       o.payment_method, o.total_amount, o.order_status
FROM "order" o
JOIN customer c ON o.customer_id = c.customer_id
ORDER BY o.order_date DESC
LIMIT 20;
```

#### E. Query Shipping Analytics

```sql
-- Shipping Status Distribution
SELECT shipping_status, COUNT(*) as count
FROM shipping
GROUP BY shipping_status;

-- Shipping Analysis by Country (JOIN 4 tabel)
SELECT co.name as country, 
       COUNT(s.shipping_id) as total_shipments,
       AVG(s.shipping_cost) as avg_cost,
       SUM(CASE WHEN s.shipping_status = 'Delivered' THEN 1 ELSE 0 END) as delivered
FROM shipping s
JOIN customer_address ca ON s.customer_address_id = ca.customer_address_id
JOIN customer c ON ca.customer_id = c.customer_id
JOIN country co ON c.country_id = co.country_id
GROUP BY co.name
ORDER BY total_shipments DESC
LIMIT 15;
```

#### F. Query Review Analytics

```sql
-- Rating Distribution
SELECT rating, COUNT(*) as count
FROM product_review
GROUP BY rating
ORDER BY rating;

-- Reviews Over Time
SELECT DATE_TRUNC('month', review_date) as month, 
       COUNT(*) as reviews,
       AVG(rating) as avg_rating
FROM product_review
WHERE review_date IS NOT NULL
GROUP BY DATE_TRUNC('month', review_date)
ORDER BY month;

-- Average Rating by Category
SELECT c.name as category, 
       COUNT(pr.review_id) as total_reviews,
       AVG(pr.rating) as avg_rating
FROM product_review pr
JOIN product p ON pr.product_id = p.product_id
JOIN category c ON p.category_id = c.category_id
GROUP BY c.name
ORDER BY avg_rating DESC;

-- Top Rated Products (dengan minimum reviews)
SELECT p.name as product, c.name as category, b.name as brand,
       COUNT(pr.review_id) as total_reviews,
       AVG(pr.rating) as avg_rating
FROM product_review pr
JOIN product p ON pr.product_id = p.product_id
JOIN category c ON p.category_id = c.category_id
JOIN brand b ON p.brand_id = b.brand_id
GROUP BY p.name, c.name, b.name
HAVING COUNT(pr.review_id) >= 5
ORDER BY avg_rating DESC, total_reviews DESC
LIMIT 10;
```

#### G. Query Store & Brand Analytics

```sql
-- Store Performance (JOIN 3 tabel)
SELECT s.name as store,
       COUNT(DISTINCT p.product_id) as products,
       SUM(oi.quantity) as items_sold,
       SUM(oi.quantity * oi.unit_price) as revenue
FROM store s
JOIN product p ON s.store_id = p.store_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY s.name
ORDER BY revenue DESC;

-- Brand Performance (JOIN 4 tabel)
SELECT b.name as brand,
       COUNT(DISTINCT p.product_id) as products,
       SUM(oi.quantity) as items_sold,
       SUM(oi.quantity * oi.unit_price) as revenue,
       AVG(pr.rating) as avg_rating
FROM brand b
JOIN product p ON b.brand_id = p.brand_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN product_review pr ON p.product_id = pr.product_id
GROUP BY b.name
ORDER BY revenue DESC;
```

#### H. Query Stock Movement

```sql
-- Movement Type Distribution
SELECT movement_type, COUNT(*) as count,
       SUM(ABS(quantity_change)) as total_quantity
FROM stock
GROUP BY movement_type;

-- Stock Movements Over Time
SELECT DATE_TRUNC('month', change_date) as month,
       movement_type,
       SUM(ABS(quantity_change)) as quantity
FROM stock
WHERE change_date IS NOT NULL
GROUP BY DATE_TRUNC('month', change_date), movement_type
ORDER BY month;

-- Stock Movement by Category
SELECT c.name as category, st.movement_type,
       COUNT(*) as movements,
       SUM(ABS(st.quantity_change)) as total_quantity
FROM stock st
JOIN product p ON st.product_id = p.product_id
JOIN category c ON p.category_id = c.category_id
GROUP BY c.name, st.movement_type
ORDER BY total_quantity DESC;
```

---

## 3.4. Visualisasi Data

### 3.4.1. Teknologi Visualisasi

Dashboard visualisasi dibangun menggunakan teknologi berikut:

| Komponen | Teknologi | Keterangan |
|----------|-----------|------------|
| Framework | Streamlit | Python web framework untuk data apps |
| Charting Library | Plotly | Interactive charts dan graphs |
| Database Connection | SQLAlchemy | ORM untuk koneksi PostgreSQL |
| Styling | Custom CSS | Tema dark mode |

### 3.4.2. Struktur Dashboard

Dashboard terdiri dari 9 halaman utama:

1. **🏠 Overview Dashboard**
   - KPI Metrics (Customers, Orders, Revenue, Products, Rating)
   - Orders Trend Over Time (Line Chart)
   - Payment Method Distribution (Pie Chart)
   - Top Categories by Revenue (Horizontal Bar Chart)
   - Top Brands by Revenue (Horizontal Bar Chart)

2. **👥 Customer Analytics**
   - Customer Metrics
   - Top Countries by Customers (Bar Chart)
   - Gender Distribution (Donut Chart)
   - Customer Signups Over Time (Area Chart)
   - Top Customers Table

3. **📦 Product Analytics**
   - Product Metrics (Products, Categories, Brands, Stores)
   - Products per Category (Bar Chart)
   - Products per Brand (Pie Chart)
   - Products per Store (Bar Chart)
   - Price Distribution (Histogram)
   - Best Selling Products Table

4. **🛍️ Order Analytics**
   - Order Metrics (Orders, Revenue, Avg Order Value, Items Sold)
   - Order Status Distribution (Pie Chart)
   - Revenue by Payment Method (Bar Chart)
   - Monthly Revenue Trend (Combined Bar + Line Chart)
   - Recent Orders Table

5. **🚚 Shipping Analytics**
   - Shipping Metrics (Shipments, Avg Cost, Delivered)
   - Shipping Status Distribution (Pie Chart)
   - Shipping Cost Distribution (Histogram)
   - Shipping by Country Table

6. **⭐ Review Analytics**
   - Review Metrics (Total Reviews, Avg Rating, 5-Star Reviews)
   - Rating Distribution (Bar Chart)
   - Reviews Over Time (Line Chart)
   - Average Rating by Category (Bar Chart)
   - Top Rated Products Table

7. **📊 Store & Brand Analytics**
   - Store Performance (Bar Chart + Table)
   - Brand Performance Matrix (Scatter Plot + Table)

8. **📈 Stock Movement**
   - Stock Metrics (Movements, Stock In, Stock Out)
   - Movement Type Distribution (Pie Chart)
   - Stock Movements Over Time (Multi-line Chart)
   - Stock Movement by Category (Grouped Bar Chart)

9. **🔍 Data Explorer**
   - Table Preview untuk 12 tabel
   - Custom SQL Query Editor
   - Export CSV

### 3.4.3. Grafik

#### A. Line Charts
- Orders Trend Over Time
- Customer Signups Over Time
- Reviews Over Time
- Stock Movements Over Time

#### B. Bar Charts
- Top Categories by Revenue
- Top Brands by Revenue
- Top Countries by Customers
- Products per Category/Brand/Store
- Rating Distribution
- Store/Brand Performance

#### C. Pie/Donut Charts
- Payment Method Distribution
- Gender Distribution
- Order Status Distribution
- Shipping Status Distribution
- Movement Type Distribution

#### D. Histograms
- Price Distribution
- Shipping Cost Distribution

#### E. Scatter Plots
- Brand Performance Matrix (Items Sold vs Revenue)

#### F. Combined Charts
- Monthly Revenue Trend (Bar + Line)

### 3.4.4. Tabel

Setiap halaman menyertakan tabel data untuk detail informasi:

| Halaman | Tabel |
|---------|-------|
| Customer Analytics | Top 10 Customers by Spending |
| Product Analytics | Top 10 Best Selling Products |
| Order Analytics | 20 Recent Orders |
| Shipping Analytics | Shipping Analysis by Country |
| Review Analytics | Top Rated Products |
| Store & Brand | Store/Brand Performance |
| Data Explorer | Preview semua tabel |

---

## 3.5. Interpretasi Hasil

### 3.5.1. Insight Pelanggan (Customer)

Berdasarkan hasil analisis data pelanggan:

1. **Distribusi Geografis**: Terdapat 243 negara yang tercatat dalam sistem dengan distribusi pelanggan yang beragam.

2. **Demografi Gender**: Distribusi gender menunjukkan proporsi yang relatif seimbang antara Male, Female, dan Other.

3. **Tren Pendaftaran**: Grafik signups menunjukkan pola pertumbuhan pelanggan dari waktu ke waktu.

### 3.5.2. Insight Produk (Product)

1. **Kategori Produk**: Terdapat 6 kategori utama (Books, Beauty, Toys, Electronics, Clothing, Home) dengan distribusi produk yang berbeda-beda.

2. **Merek**: 4 brand (BrandA, BrandB, BrandC, BrandD) dengan kontribusi revenue yang dapat dibandingkan.

3. **Distribusi Harga**: Histogram harga menunjukkan sebaran harga produk dalam sistem.

### 3.5.3. Insight Transaksi (Order)

1. **Volume Transaksi**: Total 20,117 order dengan 50,233 item terjual.

2. **Metode Pembayaran**: Distribusi antara Cash, Credit Card, dan Bank Transfer.

3. **Status Order**: Mayoritas order berstatus Delivered (sekitar 70%).

4. **Tren Bulanan**: Pola revenue dan jumlah order per bulan dapat dianalisis untuk identifikasi seasonality.

### 3.5.4. Insight Pengiriman (Shipping)

1. **Status Pengiriman**: Sekitar 65% pengiriman berstatus Delivered.

2. **Biaya Pengiriman**: Rata-rata biaya pengiriman berkisar $5-$50.

3. **Analisis per Negara**: Performa pengiriman dapat dibandingkan antar negara.

### 3.5.5. Insight Review Produk

1. **Rating Rata-rata**: Nilai rating berkisar 1-5 dengan distribusi tertentu.

2. **Tren Review**: Pola review dari waktu ke waktu menunjukkan engagement pelanggan.

3. **Rating per Kategori**: Perbandingan kepuasan pelanggan antar kategori produk.

### 3.5.6. Insight Performa Toko & Merek

1. **Store Performance**: 10 toko dengan performa berbeda berdasarkan revenue dan items sold.

2. **Brand Performance**: Matrix scatter plot menunjukkan korelasi antara volume penjualan, revenue, dan rating.

### 3.5.7. Insight Stock Movement

1. **Tipe Movement**: Distribusi antara IN (stok masuk), OUT (stok keluar), dan ADJUSTMENT.

2. **Tren Pergerakan**: Pola pergerakan stok per bulan.

3. **Movement per Kategori**: Kategori mana yang memiliki perputaran stok tertinggi.

---

## Ringkasan Implementasi

| Aspek | Detail |
|-------|--------|
| **Database** | Supabase (PostgreSQL 17) |
| **Total Tabel** | 12 tabel relasional |
| **Total Records** | ~146,000+ records |
| **Foreign Keys** | 12 relasi FK |
| **Indexes** | 19 indexes untuk optimasi |
| **Visualisasi** | 9 halaman dashboard |
| **Jenis Chart** | 6 tipe (Line, Bar, Pie, Histogram, Scatter, Combined) |
| **Framework** | Streamlit + Plotly |

