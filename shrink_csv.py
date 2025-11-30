import pandas as pd
import os

# =============================================================================
# CONFIG: Adjust MAX_CUSTOMERS to control total dataset size
# With 5000 customers, expect ~85k total rows across all tables
# =============================================================================
MAX_CUSTOMERS = 5_000  # Reduced from 50k to keep data manageable

# Create output directory
os.makedirs("resized", exist_ok=True)

print("Loading original CSV files...")

# 1. Ambil subset customer (random sample)
print("  - Loading customers.csv...")
customers = pd.read_csv("customers.csv")
customers_small = customers.sample(n=MAX_CUSTOMERS, random_state=42)
customer_ids = set(customers_small["customer_id"])
print(f"    Selected {len(customers_small):,} customers")

# 2. Filter orders berdasarkan customer_id tadi
print("  - Loading orders.csv...")
orders = pd.read_csv("orders.csv")
orders_small = orders[orders["customer_id"].isin(customer_ids)]
order_ids = set(orders_small["order_id"])
print(f"    Filtered to {len(orders_small):,} orders")

# 3. Filter order_items berdasarkan order_id
print("  - Loading order_items.csv...")
order_items = pd.read_csv("order_items.csv")
order_items_small = order_items[order_items["order_id"].isin(order_ids)]
product_ids = set(order_items_small["product_id"])
print(f"    Filtered to {len(order_items_small):,} order_items")

# 4. Filter products berdasarkan product_ids yang kepakai
print("  - Loading products.csv...")
products = pd.read_csv("products.csv")
products_small = products[products["product_id"].isin(product_ids)]
print(f"    Filtered to {len(products_small):,} products")

# 5. Filter product_reviews
print("  - Loading product_reviews.csv...")
reviews = pd.read_csv("product_reviews.csv")
reviews_small = reviews[
    reviews["customer_id"].isin(customer_ids)
    & reviews["product_id"].isin(product_ids)
]
print(f"    Filtered to {len(reviews_small):,} reviews")

# 6. Simpan ke folder resized
print("\nSaving to resized/ folder...")
customers_small.to_csv("resized/customers.csv", index=False)
products_small.to_csv("resized/products.csv", index=False)
orders_small.to_csv("resized/orders.csv", index=False)
order_items_small.to_csv("resized/order_items.csv", index=False)
reviews_small.to_csv("resized/product_reviews.csv", index=False)

# Summary
print("\n" + "=" * 60)
print("SHRINK COMPLETE - Summary:")
print("=" * 60)
print(f"  customers.csv      : {len(customers_small):>10,} rows")
print(f"  products.csv       : {len(products_small):>10,} rows")
print(f"  orders.csv         : {len(orders_small):>10,} rows")
print(f"  order_items.csv    : {len(order_items_small):>10,} rows")
print(f"  product_reviews.csv: {len(reviews_small):>10,} rows")
print("-" * 60)
total = len(customers_small) + len(products_small) + len(orders_small) + len(order_items_small) + len(reviews_small)
print(f"  TOTAL              : {total:>10,} rows")
print("=" * 60)
print("\nFiles saved to: resized/")
