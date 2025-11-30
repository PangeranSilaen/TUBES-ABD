# 📊 Supabase E-Commerce Database Setup - Summary

**Date:** December 1, 2025  
**Project ID:** `lokizaoluolkdetelmfd`  
**Dataset Source:** Kaggle - Synthetic E-Commerce Relational Datasets  
**Status:** ✅ COMPLETE

---

## 📋 Task Overview

Membuat e-commerce database di Supabase dari Kaggle dataset yang sangat besar (34 juta rows) dan dioptimalkan untuk keperluan visualisasi dan testing query SQL (hanya ~103k rows final).

---

## 🔄 Process yang Dilakukan

### 1. **Dataset Analysis**
- Analyzed original CSV files dari Kaggle:
  - `customers.csv`: 2,000,000 rows
  - `products.csv`: 20,000 rows
  - `orders.csv`: 8,000,000 rows
  - `order_items.csv`: 20,000,000 rows
  - `product_reviews.csv`: 4,000,000 rows
  - **Total: 34,000,000 rows**

### 2. **Data Shrinking Strategy**
**Problem:** Dataset terlalu besar (34M rows) untuk keperluan pembelajaran & presentasi

**Solution:** 
- Mulai dari 5,000 random customers (dengan seed 42 untuk reproducibility)
- Filter cascading dari customer → orders → order_items → products → reviews
- Menjaga integritas relasi (setiap data punya foreign key relation)

**Script:** `shrink_csv.py`
```python
MAX_CUSTOMERS = 5_000
# Cascading filter: customers → orders → order_items → products → reviews
```

### 3. **Final Dataset**
Setelah shrinking, dataset final:
| Tabel | Rows |
|-------|------|
| customers | 5,000 |
| products | 18,356 |
| orders | 20,117 |
| order_items | 50,233 |
| product_reviews | 9,221 |
| **TOTAL** | **102,927 rows** |

**Reduction: 99.7%** (34M → 103k rows)

Files generated di folder `resized/`:
- `customers.csv`
- `products.csv`
- `orders.csv`
- `order_items.csv`
- `product_reviews.csv`

### 4. **Database Setup di Supabase**

#### Step 1: Create Tables (via Supabase UI)
- Upload semua 5 CSV files melalui Supabase Studio import feature
- Supabase otomatis create tables dengan format:
  - Semua columns awal: `text` atau `bigint`
  - Tidak ada PRIMARY KEY
  - Tidak ada FOREIGN KEY

#### Step 2: Alter Tables - Set Primary Keys
```sql
ALTER TABLE customers ADD PRIMARY KEY (customer_id);
ALTER TABLE products ADD PRIMARY KEY (product_id);
ALTER TABLE orders ADD PRIMARY KEY (order_id);
ALTER TABLE order_items ADD PRIMARY KEY (order_item_id);
ALTER TABLE product_reviews ADD PRIMARY KEY (review_id);
```

#### Step 3: Fix Data Types
```sql
-- DATE columns
ALTER TABLE customers ALTER COLUMN signup_date TYPE date USING signup_date::date;
ALTER TABLE orders ALTER COLUMN order_date TYPE date USING order_date::date;
ALTER TABLE product_reviews ALTER COLUMN review_date TYPE date USING review_date::date;

-- NUMERIC columns
ALTER TABLE orders ALTER COLUMN total_amount TYPE numeric(10,2) USING total_amount::numeric;

-- Set NOT NULL on important columns
ALTER TABLE customers ALTER COLUMN name SET NOT NULL;
ALTER TABLE customers ALTER COLUMN email SET NOT NULL;
ALTER TABLE orders ALTER COLUMN customer_id SET NOT NULL;
ALTER TABLE order_items ALTER COLUMN order_id SET NOT NULL;
ALTER TABLE order_items ALTER COLUMN product_id SET NOT NULL;
ALTER TABLE product_reviews ALTER COLUMN product_id SET NOT NULL;
ALTER TABLE product_reviews ALTER COLUMN customer_id SET NOT NULL;
```

#### Step 4: Add Foreign Key Constraints
```sql
-- orders.customer_id → customers.customer_id
ALTER TABLE orders
ADD CONSTRAINT fk_orders_customer
FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE;

-- order_items.order_id → orders.order_id
ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_order
FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE;

-- order_items.product_id → products.product_id
ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_product
FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE;

-- product_reviews.product_id → products.product_id
ALTER TABLE product_reviews
ADD CONSTRAINT fk_reviews_product
FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE;

-- product_reviews.customer_id → customers.customer_id
ALTER TABLE product_reviews
ADD CONSTRAINT fk_reviews_customer
FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE;
```

---

## 📊 Final Database Schema

### **customers** (5,000 rows)
| Column | Type | Constraints |
|--------|------|-------------|
| customer_id | bigint | PRIMARY KEY |
| name | text | NOT NULL |
| email | text | NOT NULL |
| gender | text | |
| signup_date | date | |
| country | text | |

### **products** (18,356 rows)
| Column | Type | Constraints |
|--------|------|-------------|
| product_id | bigint | PRIMARY KEY |
| product_name | text | |
| category | text | |
| price | numeric | |
| stock_quantity | bigint | |
| brand | text | |

### **orders** (20,117 rows)
| Column | Type | Constraints |
|--------|------|-------------|
| order_id | bigint | PRIMARY KEY |
| customer_id | bigint | NOT NULL, FK→customers |
| order_date | date | |
| total_amount | numeric | |
| payment_method | text | |
| shipping_country | text | |

### **order_items** (50,233 rows)
| Column | Type | Constraints |
|--------|------|-------------|
| order_item_id | bigint | PRIMARY KEY |
| order_id | bigint | NOT NULL, FK→orders |
| product_id | bigint | NOT NULL, FK→products |
| quantity | bigint | NOT NULL |
| unit_price | numeric | |

### **product_reviews** (9,221 rows)
| Column | Type | Constraints |
|--------|------|-------------|
| review_id | bigint | PRIMARY KEY |
| product_id | bigint | NOT NULL, FK→products |
| customer_id | bigint | NOT NULL, FK→customers |
| rating | bigint | NOT NULL |
| review_text | text | |
| review_date | date | |

---

## 🔗 Relationship Diagram

```
┌──────────────┐
│  customers   │
│ (5,000)      │
└──────────────┘
       │
       ├─────────────────────┬────────────────────┐
       │                     │                    │
       ▼                     ▼                    ▼
┌──────────────┐      ┌─────────────┐    ┌──────────────────┐
│   orders     │      │   product   │    │ product_reviews  │
│ (20,117)     │      │   reviews   │    │ (9,221)          │
└──────────────┘      │ (9,221)     │    └──────────────────┘
       │              └─────────────┘
       │
       ▼
┌──────────────────┐
│  order_items     │
│ (50,233)         │
│  ├─ order_id     ├──→ orders
│  └─ product_id   ├──→ products
└──────────────────┘
```

**Relasi:**
- `customers` → `orders` (1:N) - One customer has many orders
- `customers` → `product_reviews` (1:N) - One customer writes many reviews
- `products` → `order_items` (1:N) - One product in many order items
- `products` → `product_reviews` (1:N) - One product has many reviews
- `orders` → `order_items` (1:N) - One order has many items

---

## ✅ Verification Queries

Gunakan query berikut untuk verify integritas data:

### 1. Check Total Rows
```sql
SELECT 'customers' as table_name, COUNT(*) as row_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'product_reviews', COUNT(*) FROM product_reviews;
```

### 2. Check Foreign Key Integrity
```sql
-- Check orders dengan customer_id yang valid
SELECT COUNT(*) as orders_with_valid_customer 
FROM orders o
WHERE EXISTS (SELECT 1 FROM customers c WHERE c.customer_id = o.customer_id);

-- Check order_items dengan order_id dan product_id yang valid
SELECT COUNT(*) as order_items_with_valid_refs
FROM order_items oi
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.order_id = oi.order_id)
AND EXISTS (SELECT 1 FROM products p WHERE p.product_id = oi.product_id);

-- Check product_reviews dengan foreign keys yang valid
SELECT COUNT(*) as reviews_with_valid_refs
FROM product_reviews pr
WHERE EXISTS (SELECT 1 FROM customers c WHERE c.customer_id = pr.customer_id)
AND EXISTS (SELECT 1 FROM products p WHERE p.product_id = pr.product_id);
```

### 3. Sample Query - Customer Orders
```sql
SELECT 
  c.name,
  COUNT(o.order_id) as order_count,
  SUM(o.total_amount) as total_spent,
  MAX(o.order_date) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 10;
```

### 4. Sample Query - Product Performance
```sql
SELECT 
  p.product_name,
  p.category,
  COUNT(DISTINCT oi.order_id) as times_ordered,
  SUM(oi.quantity) as total_quantity_sold,
  AVG(pr.rating) as avg_rating
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY times_ordered DESC
LIMIT 10;
```

---

## 📁 File Structure

```
d:\Data\Downloads\archive\csv\
├── shrink_csv.py              # Script untuk shrink dataset
├── resized/
│   ├── customers.csv          # 5,000 rows
│   ├── products.csv           # 18,356 rows
│   ├── orders.csv             # 20,117 rows
│   ├── order_items.csv        # 50,233 rows
│   └── product_reviews.csv    # 9,221 rows
├── customers.csv              # Original (2M rows)
├── products.csv               # Original (20k rows)
├── orders.csv                 # Original (8M rows)
├── order_items.csv            # Original (20M rows)
├── product_reviews.csv        # Original (4M rows)
├── ERD.png                    # Entity Relationship Diagram
├── upload_sequence.json       # Upload metadata
└── SETUP_SUMMARY.md           # File ini

```

---

## 🚀 Selanjutnya

Database Anda sudah siap untuk:
1. ✅ **Testing Query SQL** - Gunakan sample queries di atas
2. ✅ **Data Visualization** - Connect ke tools BI (Metabase, Looker, Tableau)
3. ✅ **Presentation ke Dosen** - ~103k rows cukup untuk demo
4. ✅ **Scale ke Production** - Struktur sudah optimize, bisa replace dengan data lebih besar

---

## 📌 Catatan Penting

- **Reproducibility:** Script menggunakan `random_state=42`, jadi hasil selalu konsisten
- **Data Integrity:** Semua relasi FK dengan `ON DELETE CASCADE`
- **Performance:** ~103k rows optimal untuk development & testing
- **Scalability:** Schema sudah siap untuk dataset lebih besar

---

**Setup completed successfully! 🎉**
