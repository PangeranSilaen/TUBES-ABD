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
BASE_PATH = r"d:\Data\Documents\Semester 5\Administrasi Basis Data\Tugas Besar"
INPUT_PATH = os.path.join(BASE_PATH, "resized")
OUTPUT_PATH = os.path.join(BASE_PATH, "resized_new")

# Buat folder output jika belum ada
os.makedirs(OUTPUT_PATH, exist_ok=True)

print("=" * 60)
print("GENERATE TABEL BARU SESUAI ERD")
print("=" * 60)

# ============================================================
# 1. LOAD DATA EXISTING
# ============================================================
print("\n[1] Loading data existing...")

customers_df = pd.read_csv(os.path.join(INPUT_PATH, "customers.csv"))
products_df = pd.read_csv(os.path.join(INPUT_PATH, "products.csv"))
orders_df = pd.read_csv(os.path.join(INPUT_PATH, "orders.csv"))
order_items_df = pd.read_csv(os.path.join(INPUT_PATH, "order_items.csv"))
product_reviews_df = pd.read_csv(os.path.join(INPUT_PATH, "product_reviews.csv"))

print(f"   - customers: {len(customers_df)} rows")
print(f"   - products: {len(products_df)} rows")
print(f"   - orders: {len(orders_df)} rows")
print(f"   - order_items: {len(order_items_df)} rows")
print(f"   - product_reviews: {len(product_reviews_df)} rows")

# ============================================================
# 2. GENERATE TABEL COUNTRY
# ============================================================
print("\n[2] Generating tabel COUNTRY...")

# Extract unique countries dari customers
unique_countries = customers_df['country'].dropna().unique()
country_df = pd.DataFrame({
    'country_id': range(1, len(unique_countries) + 1),
    'name': unique_countries
})

# Buat mapping country name -> country_id
country_mapping = dict(zip(country_df['name'], country_df['country_id']))

print(f"   - Total countries: {len(country_df)}")
country_df.to_csv(os.path.join(OUTPUT_PATH, "country.csv"), index=False)

# ============================================================
# 3. GENERATE TABEL CATEGORY
# ============================================================
print("\n[3] Generating tabel CATEGORY...")

unique_categories = products_df['category'].dropna().unique()
category_df = pd.DataFrame({
    'category_id': range(1, len(unique_categories) + 1),
    'name': unique_categories
})

# Buat mapping
category_mapping = dict(zip(category_df['name'], category_df['category_id']))

print(f"   - Total categories: {len(category_df)}")
category_df.to_csv(os.path.join(OUTPUT_PATH, "category.csv"), index=False)

# ============================================================
# 4. GENERATE TABEL BRAND
# ============================================================
print("\n[4] Generating tabel BRAND...")

unique_brands = products_df['brand'].dropna().unique()
brand_df = pd.DataFrame({
    'brand_id': range(1, len(unique_brands) + 1),
    'name': unique_brands
})

# Buat mapping
brand_mapping = dict(zip(brand_df['name'], brand_df['brand_id']))

print(f"   - Total brands: {len(brand_df)}")
brand_df.to_csv(os.path.join(OUTPUT_PATH, "brand.csv"), index=False)

# ============================================================
# 5. GENERATE TABEL STORE (Dummy)
# ============================================================
print("\n[5] Generating tabel STORE (dummy)...")

# Generate beberapa store dummy
store_names = [
    "TechMart Central", "Fashion Hub", "BookWorm Paradise", 
    "Beauty Corner", "Toy Kingdom", "Home Essentials",
    "Sports Zone", "Gadget World", "Style Avenue", "Daily Needs"
]

store_df = pd.DataFrame({
    'store_id': range(1, len(store_names) + 1),
    'name': store_names
})

print(f"   - Total stores: {len(store_df)}")
store_df.to_csv(os.path.join(OUTPUT_PATH, "store.csv"), index=False)

# ============================================================
# 6. UPDATE TABEL CUSTOMER (tambah country_id)
# ============================================================
print("\n[6] Updating tabel CUSTOMER...")

customer_new_df = customers_df.copy()
customer_new_df['country_id'] = customer_new_df['country'].map(country_mapping)

# Reorder columns sesuai ERD: customer_id, country_id, name, email, gender, signup_date
customer_new_df = customer_new_df[['customer_id', 'country_id', 'name', 'email', 'gender', 'signup_date']]

print(f"   - Total customers: {len(customer_new_df)}")
customer_new_df.to_csv(os.path.join(OUTPUT_PATH, "customer.csv"), index=False)

# ============================================================
# 7. GENERATE TABEL CUSTOMER_ADDRESS (Dummy)
# ============================================================
print("\n[7] Generating tabel CUSTOMER_ADDRESS (dummy)...")

# Generate 1-3 alamat per customer (untuk sebagian customer saja)
sample_customers = customer_new_df['customer_id'].sample(frac=0.7, random_state=42).tolist()

address_templates = [
    "Jl. {} No. {}, RT {}/RW {}",
    "{} Street No. {}, Block {}",
    "Kompleks {} Blok {} No. {}",
    "{} Avenue, Apt {}",
    "Perumahan {} No. {}"
]

street_names = ["Merdeka", "Sudirman", "Gatot Subroto", "Ahmad Yani", "Diponegoro", 
                "Imam Bonjol", "Kartini", "Veteran", "Pahlawan", "Mangga", "Melati",
                "Oak", "Pine", "Maple", "Cedar", "Willow"]

addresses = []
address_id = 1

for cust_id in sample_customers:
    num_addresses = random.randint(1, 2)
    for _ in range(num_addresses):
        template = random.choice(address_templates)
        street = random.choice(street_names)
        
        if "{}" in template:
            parts = template.count("{}")
            if parts == 4:
                addr = template.format(street, random.randint(1, 200), 
                                       random.randint(1, 20), random.randint(1, 10))
            elif parts == 3:
                addr = template.format(street, random.choice("ABCDEFGH"), random.randint(1, 50))
            elif parts == 2:
                addr = template.format(street, random.randint(1, 500))
            else:
                addr = template.format(street)
        else:
            addr = template
            
        addresses.append({
            'customer_address_id': address_id,
            'customer_id': cust_id,
            'address': addr
        })
        address_id += 1

customer_address_df = pd.DataFrame(addresses)

print(f"   - Total addresses: {len(customer_address_df)}")
customer_address_df.to_csv(os.path.join(OUTPUT_PATH, "customer_address.csv"), index=False)

# Buat mapping customer_id -> customer_address_id (ambil yang pertama)
customer_address_mapping = customer_address_df.groupby('customer_id')['customer_address_id'].first().to_dict()

# ============================================================
# 8. GENERATE TABEL SHIPPING (Dummy)
# ============================================================
print("\n[8] Generating tabel SHIPPING (dummy)...")

shipping_statuses = ['Pending', 'Processing', 'Shipped', 'In Transit', 'Delivered', 'Cancelled']
shipping_status_weights = [0.05, 0.05, 0.1, 0.1, 0.65, 0.05]  # Mostly delivered

shippings = []
shipping_id = 1

# Generate shipping untuk setiap order
for idx, order in orders_df.iterrows():
    cust_id = order['customer_id']
    
    # Cari customer_address_id, jika tidak ada generate default
    if cust_id in customer_address_mapping:
        addr_id = customer_address_mapping[cust_id]
    else:
        # Untuk customer yang tidak punya address, buat address baru
        new_addr_id = len(customer_address_df) + len([s for s in shippings if 'new_address' in str(s.get('note', ''))]) + 1
        addr_id = new_addr_id
        # Tambahkan ke customer_address_df
        new_address = {
            'customer_address_id': new_addr_id,
            'customer_id': cust_id,
            'address': f"Default Address for Customer {cust_id}"
        }
        customer_address_df = pd.concat([customer_address_df, pd.DataFrame([new_address])], ignore_index=True)
        customer_address_mapping[cust_id] = new_addr_id
    
    # Generate shipping cost (5-50)
    shipping_cost = round(random.uniform(5, 50), 2)
    
    # Generate shipping status
    status = random.choices(shipping_statuses, weights=shipping_status_weights)[0]
    
    shippings.append({
        'shipping_id': shipping_id,
        'customer_address_id': addr_id,
        'shipping_status': status,
        'shipping_cost': shipping_cost
    })
    shipping_id += 1

shipping_df = pd.DataFrame(shippings)

print(f"   - Total shippings: {len(shipping_df)}")
shipping_df.to_csv(os.path.join(OUTPUT_PATH, "shipping.csv"), index=False)

# Update customer_address.csv dengan data baru
customer_address_df.to_csv(os.path.join(OUTPUT_PATH, "customer_address.csv"), index=False)
print(f"   - Updated customer_address: {len(customer_address_df)} rows")

# ============================================================
# 9. UPDATE TABEL PRODUCT (tambah FK)
# ============================================================
print("\n[9] Updating tabel PRODUCT...")

product_new_df = products_df.copy()

# Tambah store_id (random assignment)
product_new_df['store_id'] = np.random.randint(1, len(store_df) + 1, size=len(product_new_df))

# Tambah category_id
product_new_df['category_id'] = product_new_df['category'].map(category_mapping)

# Tambah brand_id
product_new_df['brand_id'] = product_new_df['brand'].map(brand_mapping)

# Reorder columns sesuai ERD: product_id, store_id, category_id, brand_id, name, price, stock_quantity
product_new_df = product_new_df.rename(columns={'product_name': 'name'})
product_new_df = product_new_df[['product_id', 'store_id', 'category_id', 'brand_id', 'name', 'price', 'stock_quantity']]

print(f"   - Total products: {len(product_new_df)}")
product_new_df.to_csv(os.path.join(OUTPUT_PATH, "product.csv"), index=False)

# ============================================================
# 10. UPDATE TABEL ORDER (tambah shipping_id, order_status)
# ============================================================
print("\n[10] Updating tabel ORDER...")

order_statuses = ['Pending', 'Confirmed', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Refunded']
order_status_weights = [0.03, 0.05, 0.05, 0.07, 0.70, 0.05, 0.05]

order_new_df = orders_df.copy()

# Tambah shipping_id (1-to-1 dengan order)
order_new_df['shipping_id'] = range(1, len(order_new_df) + 1)

# Tambah order_status
order_new_df['order_status'] = random.choices(order_statuses, weights=order_status_weights, k=len(order_new_df))

# Reorder columns sesuai ERD: order_id, customer_id, shipping_id, order_date, payment_method, total_amount, order_status
order_new_df = order_new_df[['order_id', 'customer_id', 'shipping_id', 'order_date', 'payment_method', 'total_amount', 'order_status']]

print(f"   - Total orders: {len(order_new_df)}")
order_new_df.to_csv(os.path.join(OUTPUT_PATH, "order.csv"), index=False)

# ============================================================
# 11. UPDATE TABEL ORDER_ITEMS (rename column)
# ============================================================
print("\n[11] Updating tabel ORDER_ITEMS...")

order_items_new_df = order_items_df.copy()
order_items_new_df = order_items_new_df.rename(columns={'order_item_id': 'order_items_id'})

# Reorder: order_items_id, product_id, order_id, quantity, unit_price
order_items_new_df = order_items_new_df[['order_items_id', 'product_id', 'order_id', 'quantity', 'unit_price']]

print(f"   - Total order_items: {len(order_items_new_df)}")
order_items_new_df.to_csv(os.path.join(OUTPUT_PATH, "order_items.csv"), index=False)

# ============================================================
# 12. UPDATE TABEL PRODUCT_REVIEW (sudah sesuai ERD)
# ============================================================
print("\n[12] Copying tabel PRODUCT_REVIEW...")

product_review_new_df = product_reviews_df.copy()
# Columns sudah sesuai: review_id, product_id, customer_id, rating, review_text, review_date

print(f"   - Total product_reviews: {len(product_review_new_df)}")
product_review_new_df.to_csv(os.path.join(OUTPUT_PATH, "product_review.csv"), index=False)

# ============================================================
# 13. GENERATE TABEL STOCK (Dummy - Riwayat Perubahan Stok)
# ============================================================
print("\n[13] Generating tabel STOCK (dummy)...")

movement_types = ['IN', 'OUT', 'ADJUSTMENT']
movement_weights = [0.4, 0.5, 0.1]

stocks = []
stock_id = 1

# Generate beberapa record stock movement untuk sebagian produk
sample_products = product_new_df['product_id'].sample(frac=0.3, random_state=42).tolist()

start_date = datetime(2021, 1, 1)
end_date = datetime(2025, 12, 1)

for prod_id in sample_products:
    # Generate 1-5 stock movements per product
    num_movements = random.randint(1, 5)
    
    for _ in range(num_movements):
        movement_type = random.choices(movement_types, weights=movement_weights)[0]
        
        if movement_type == 'IN':
            qty_change = random.randint(10, 500)
        elif movement_type == 'OUT':
            qty_change = -random.randint(1, 100)
        else:  # ADJUSTMENT
            qty_change = random.randint(-50, 50)
        
        # Random date
        days_diff = (end_date - start_date).days
        change_date = start_date + timedelta(days=random.randint(0, days_diff))
        
        stocks.append({
            'stock_id': stock_id,
            'product_id': prod_id,
            'quantity_change': qty_change,
            'movement_type': movement_type,
            'change_date': change_date.strftime('%Y-%m-%d')
        })
        stock_id += 1

stock_df = pd.DataFrame(stocks)

print(f"   - Total stock movements: {len(stock_df)}")
stock_df.to_csv(os.path.join(OUTPUT_PATH, "stock.csv"), index=False)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY - Files generated di folder /resized_new:")
print("=" * 60)

files_generated = [
    ("country.csv", len(country_df)),
    ("category.csv", len(category_df)),
    ("brand.csv", len(brand_df)),
    ("store.csv", len(store_df)),
    ("customer.csv", len(customer_new_df)),
    ("customer_address.csv", len(customer_address_df)),
    ("shipping.csv", len(shipping_df)),
    ("product.csv", len(product_new_df)),
    ("order.csv", len(order_new_df)),
    ("order_items.csv", len(order_items_new_df)),
    ("product_review.csv", len(product_review_new_df)),
    ("stock.csv", len(stock_df)),
]

for filename, count in files_generated:
    print(f"   ✓ {filename:<25} : {count:>6} rows")

print("\n" + "=" * 60)
print("RELASI ANTAR TABEL (sesuai ERD.text):")
print("=" * 60)
print("""
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
""")

print("\nDone! Silakan import CSV ke Supabase.")
