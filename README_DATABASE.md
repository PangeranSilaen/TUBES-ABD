# Dokumentasi Generate Tabel Baru E-Commerce Database

## Overview

Dokumentasi ini menjelaskan proses transformasi data dari struktur lama ke struktur baru sesuai ERD yang telah direvisi setelah asistensi dengan dosen.

## Perubahan Struktur Database

### Struktur Lama (folder `/resized`)
| Tabel | Jumlah Row |
|-------|------------|
| customers.csv | 5,000 |
| products.csv | 18,356 |
| orders.csv | 20,117 |
| order_items.csv | 50,233 |
| product_reviews.csv | 9,221 |

### Struktur Baru (folder `/resized_new`)
| Tabel | Jumlah Row | Keterangan |
|-------|------------|------------|
| country.csv | 243 | Extracted dari customers.country |
| store.csv | 10 | Generated (dummy) |
| category.csv | 6 | Extracted dari products.category |
| brand.csv | 4 | Extracted dari products.brand |
| customer.csv | 5,000 | Modified (added country_id FK) |
| customer_address.csv | 6,705 | Generated (dummy) |
| shipping.csv | 20,117 | Generated (dummy) |
| product.csv | 18,356 | Modified (added store_id, category_id, brand_id FK) |
| order.csv | 20,117 | Modified (added shipping_id, order_status) |
| order_items.csv | 50,233 | Renamed column |
| product_review.csv | 9,221 | No change |
| stock.csv | 16,610 | Generated (dummy) |

## Relasi Antar Tabel (ERD)

```
Customer to country         : N to 1
Customer to customer_address: 1 to N
Customer to product_review  : 1 to N
Customer to order           : 1 to N
Shipping to order           : 1 to 1
Product_review to product   : N to 1
Order to order_items        : 1 to N
Product to order_items      : 1 to N
Product to store            : N to 1
Product to category         : N to 1
Product to brand            : N to 1
Product to stock            : 1 to N
```

## Urutan Import CSV ke Supabase

**PENTING:** Import harus dilakukan sesuai urutan berikut untuk menghindari error foreign key:

1. `country.csv`
2. `store.csv`
3. `category.csv`
4. `brand.csv`
5. `customer.csv`
6. `customer_address.csv`
7. `shipping.csv`
8. `product.csv`
9. `order.csv`
10. `order_items.csv`
11. `product_review.csv`
12. `stock.csv`

## Langkah Implementasi di Supabase

### Step 1: Jalankan DDL Script
1. Buka Supabase Dashboard → SQL Editor
2. Copy-paste isi file `supabase_ddl.sql`
3. Jalankan script untuk membuat semua tabel dan relasi

### Step 2: Import CSV
1. Buka Supabase Dashboard → Table Editor
2. Pilih tabel yang akan di-import
3. Klik "Insert" → "Import data from CSV"
4. Upload file CSV sesuai urutan di atas
5. Pastikan kolom ter-mapping dengan benar
6. Klik "Import"

### Step 3: Verifikasi Data
Jalankan query berikut untuk verifikasi:

```sql
-- Cek jumlah row tiap tabel
SELECT 'country' as tabel, COUNT(*) as jumlah FROM country
UNION ALL SELECT 'store', COUNT(*) FROM store
UNION ALL SELECT 'category', COUNT(*) FROM category
UNION ALL SELECT 'brand', COUNT(*) FROM brand
UNION ALL SELECT 'customer', COUNT(*) FROM customer
UNION ALL SELECT 'customer_address', COUNT(*) FROM customer_address
UNION ALL SELECT 'shipping', COUNT(*) FROM shipping
UNION ALL SELECT 'product', COUNT(*) FROM product
UNION ALL SELECT 'order', COUNT(*) FROM "order"
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'product_review', COUNT(*) FROM product_review
UNION ALL SELECT 'stock', COUNT(*) FROM stock;
```

## Files yang Dihasilkan

- `generate_new_tables.py` - Script Python untuk generate CSV
- `supabase_ddl.sql` - Script SQL untuk membuat tabel di Supabase
- `/resized_new/*.csv` - File CSV hasil generate (12 files)

## Catatan Teknis

1. **Data Dummy**: Tabel `store`, `customer_address`, `shipping`, dan `stock` berisi data dummy karena tidak ada di dataset asli.

2. **Foreign Key Mapping**: 
   - `country_id` di-mapping dari nama negara di customers.country
   - `category_id` dan `brand_id` di-mapping dari products
   - `store_id` di-assign secara random ke products

3. **Tabel `order`**: Menggunakan double quotes di SQL karena `order` adalah reserved keyword.
