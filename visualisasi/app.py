import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(page_title="Visualisasi E-Commerce (Supabase)", layout="wide")

def get_engine(url):
    if not url:
        return None
    return create_engine(url, connect_args={"sslmode": "require"})

engine = get_engine(DATABASE_URL)

st.title("Visualisasi Dataset E-Commerce (Supabase)")

if engine is None:
    st.error("DATABASE_URL belum diset. Silakan copy `.env.example` ke `.env` dan isi `DATABASE_URL`.")
    st.stop()

@st.cache_data(ttl=300)
def load_query(q):
    return pd.read_sql_query(q, engine)

with st.sidebar:
    st.header("Kontrol")
    table = st.selectbox("Tabel / View", ["overview", "customers", "orders", "order_items", "products", "product_reviews"])
    limit = st.number_input("Max rows (tabel view)", min_value=10, max_value=10000, value=200)

if table == "overview":
    col1, col2, col3, col4 = st.columns(4)
    total_customers = load_query("SELECT COUNT(*) AS cnt FROM customers").iloc[0,0]
    total_orders = load_query("SELECT COUNT(*) AS cnt FROM orders").iloc[0,0]
    total_revenue = load_query("SELECT COALESCE(SUM(total_amount),0) AS s FROM orders").iloc[0,0]
    avg_rating = load_query("SELECT AVG(rating) AS a FROM product_reviews").iloc[0,0]

    col1.metric("Customers", f"{int(total_customers):,}")
    col2.metric("Orders", f"{int(total_orders):,}")
    col3.metric("Total Revenue", f"Rp {float(total_revenue):,.2f}")
    col4.metric("Average Rating", f"{float(avg_rating or 0):.2f}")

    st.subheader("Orders per Day")
    q = "SELECT order_date, COUNT(*) AS cnt FROM orders GROUP BY order_date ORDER BY order_date"
    df_orders_time = load_query(q)
    if not df_orders_time.empty:
        chart = alt.Chart(df_orders_time).mark_line(point=True).encode(x='order_date:T', y='cnt:Q')
        st.altair_chart(chart, use_container_width=True)

    st.subheader("Top Products by Revenue")
    q2 = '''
    SELECT p.product_id, p.product_name, SUM(oi.quantity * oi.unit_price) AS revenue, SUM(oi.quantity) as qty
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_id, p.product_name
    ORDER BY revenue DESC
    LIMIT 10
    '''
    df_top = load_query(q2)
    if not df_top.empty:
        bar = alt.Chart(df_top).mark_bar().encode(x='revenue:Q', y=alt.Y('product_name:N', sort='-x'))
        st.altair_chart(bar, use_container_width=True)

    st.subheader("Rating Distribution")
    q3 = "SELECT rating, COUNT(*) AS cnt FROM product_reviews GROUP BY rating ORDER BY rating"
    df_rating = load_query(q3)
    if not df_rating.empty:
        bar2 = alt.Chart(df_rating).mark_bar().encode(x='rating:O', y='cnt:Q')
        st.altair_chart(bar2, use_container_width=True)

else:
    q = f"SELECT * FROM {table} LIMIT {int(limit)}"
    df = load_query(q)
    st.subheader(f"Preview: {table}")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, file_name=f"{table}.csv")
