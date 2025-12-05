import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# Baca dari Streamlit Secrets (deployment) atau .env (local)
if "DATABASE_URL" in st.secrets:
    DATABASE_URL = st.secrets["DATABASE_URL"]
else:
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard", 
    layout="wide",
    page_icon="🛒"
)

def get_engine(url):
    if not url:
        return None
    return create_engine(url, connect_args={"sslmode": "require"})

engine = get_engine(DATABASE_URL)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛒 E-Commerce Analytics Dashboard")
st.caption("Visualisasi Data dari 12 Tabel Relasional - Synthetic E-Commerce Dataset")

if engine is None:
    st.error("DATABASE_URL belum diset. Silakan copy `.env.example` ke `.env` dan isi `DATABASE_URL`.")
    st.stop()

@st.cache_data(ttl=300)
def load_query(q):
    try:
        return pd.read_sql_query(q, engine)
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=80)
    st.header("📊 Navigation")
    
    page = st.selectbox("Pilih Halaman", [
        "🏠 Overview Dashboard",
        "👥 Customer Analytics",
        "📦 Product Analytics", 
        "🛍️ Order Analytics",
        "🚚 Shipping Analytics",
        "⭐ Review Analytics",
        "📊 Store & Brand Analytics",
        "📈 Stock Movement",
        "🔍 Data Explorer"
    ])
    
    st.divider()
    st.markdown("### 📋 Tabel Database")
    tables = ["country", "store", "category", "brand", "customer", 
              "customer_address", "shipping", "product", "order", 
              "order_items", "product_review", "stock"]
    for t in tables:
        st.markdown(f"- `{t}`")

# ============================================================
# PAGE: OVERVIEW DASHBOARD
# ============================================================
if page == "🏠 Overview Dashboard":
    st.header("📊 Overview Dashboard")
    
    # KPI Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_customers = load_query("SELECT COUNT(*) AS cnt FROM customer").iloc[0,0]
    total_orders = load_query('SELECT COUNT(*) AS cnt FROM "order"').iloc[0,0]
    total_revenue = load_query('SELECT COALESCE(SUM(total_amount),0) AS s FROM "order"').iloc[0,0]
    total_products = load_query("SELECT COUNT(*) AS cnt FROM product").iloc[0,0]
    avg_rating = load_query("SELECT AVG(rating) AS a FROM product_review").iloc[0,0]

    col1.metric("👥 Total Customers", f"{int(total_customers):,}")
    col2.metric("🛍️ Total Orders", f"{int(total_orders):,}")
    col3.metric("💰 Total Revenue", f"${float(total_revenue):,.2f}")
    col4.metric("📦 Total Products", f"{int(total_products):,}")
    col5.metric("⭐ Avg Rating", f"{float(avg_rating or 0):.2f}")
    
    st.divider()
    
    # Row 2: Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Orders Trend Over Time")
        q = '''
        SELECT DATE_TRUNC('month', order_date) as month, 
               COUNT(*) AS total_orders,
               SUM(total_amount) AS revenue
        FROM "order"
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY month
        '''
        df_trend = load_query(q)
        if not df_trend.empty:
            fig = px.line(df_trend, x='month', y='total_orders', 
                         markers=True, title="Monthly Orders")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💳 Payment Method Distribution")
        q = '''
        SELECT payment_method, COUNT(*) as count
        FROM "order"
        GROUP BY payment_method
        '''
        df_payment = load_query(q)
        if not df_payment.empty:
            fig = px.pie(df_payment, values='count', names='payment_method',
                        title="Payment Methods")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    # Row 3
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Top 10 Categories by Revenue")
        q = '''
        SELECT c.name as category, 
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN product p ON oi.product_id = p.product_id
        JOIN category c ON p.category_id = c.category_id
        GROUP BY c.name
        ORDER BY revenue DESC
        LIMIT 10
        '''
        df_cat = load_query(q)
        if not df_cat.empty:
            fig = px.bar(df_cat, x='revenue', y='category', orientation='h',
                        title="Revenue by Category")
            fig.update_layout(height=350, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Top 10 Brands by Revenue")
        q = '''
        SELECT b.name as brand, 
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN product p ON oi.product_id = p.product_id
        JOIN brand b ON p.brand_id = b.brand_id
        GROUP BY b.name
        ORDER BY revenue DESC
        LIMIT 10
        '''
        df_brand = load_query(q)
        if not df_brand.empty:
            fig = px.bar(df_brand, x='revenue', y='brand', orientation='h',
                        title="Revenue by Brand", color='revenue')
            fig.update_layout(height=350, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE: CUSTOMER ANALYTICS
# ============================================================
elif page == "👥 Customer Analytics":
    st.header("👥 Customer Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    total_customers = load_query("SELECT COUNT(*) FROM customer").iloc[0,0]
    countries = load_query("SELECT COUNT(DISTINCT country_id) FROM customer").iloc[0,0]
    with_address = load_query("SELECT COUNT(DISTINCT customer_id) FROM customer_address").iloc[0,0]
    
    col1.metric("Total Customers", f"{int(total_customers):,}")
    col2.metric("Countries Covered", f"{int(countries):,}")
    col3.metric("Customers with Address", f"{int(with_address):,}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Top 15 Countries by Customers")
        q = '''
        SELECT co.name as country, COUNT(c.customer_id) as total_customers
        FROM customer c
        JOIN country co ON c.country_id = co.country_id
        GROUP BY co.name
        ORDER BY total_customers DESC
        LIMIT 15
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.bar(df, x='total_customers', y='country', orientation='h',
                        color='total_customers', color_continuous_scale='Blues')
            fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👫 Gender Distribution")
        q = '''
        SELECT gender, COUNT(*) as count
        FROM customer
        WHERE gender IS NOT NULL
        GROUP BY gender
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.pie(df, values='count', names='gender', hole=0.4)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📅 Customer Signups Over Time")
        q = '''
        SELECT DATE_TRUNC('month', signup_date) as month, COUNT(*) as signups
        FROM customer
        WHERE signup_date IS NOT NULL
        GROUP BY DATE_TRUNC('month', signup_date)
        ORDER BY month
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.area(df, x='month', y='signups', title="Monthly Signups")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🏆 Top 10 Customers by Total Spending")
    q = '''
    SELECT c.customer_id, c.name, c.email, co.name as country,
           COUNT(o.order_id) as total_orders,
           SUM(o.total_amount) as total_spent
    FROM customer c
    JOIN "order" o ON c.customer_id = o.customer_id
    JOIN country co ON c.country_id = co.country_id
    GROUP BY c.customer_id, c.name, c.email, co.name
    ORDER BY total_spent DESC
    LIMIT 10
    '''
    df = load_query(q)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ============================================================
# PAGE: PRODUCT ANALYTICS
# ============================================================
elif page == "📦 Product Analytics":
    st.header("📦 Product Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_products = load_query("SELECT COUNT(*) FROM product").iloc[0,0]
    total_categories = load_query("SELECT COUNT(*) FROM category").iloc[0,0]
    total_brands = load_query("SELECT COUNT(*) FROM brand").iloc[0,0]
    total_stores = load_query("SELECT COUNT(*) FROM store").iloc[0,0]
    
    col1.metric("Total Products", f"{int(total_products):,}")
    col2.metric("Categories", f"{int(total_categories):,}")
    col3.metric("Brands", f"{int(total_brands):,}")
    col4.metric("Stores", f"{int(total_stores):,}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Products per Category")
        q = '''
        SELECT c.name as category, COUNT(p.product_id) as product_count
        FROM product p
        JOIN category c ON p.category_id = c.category_id
        GROUP BY c.name
        ORDER BY product_count DESC
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.bar(df, x='category', y='product_count', color='product_count',
                        color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Products per Brand")
        q = '''
        SELECT b.name as brand, COUNT(p.product_id) as product_count
        FROM product p
        JOIN brand b ON p.brand_id = b.brand_id
        GROUP BY b.name
        ORDER BY product_count DESC
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.pie(df, values='product_count', names='brand',
                        title="Product Distribution by Brand")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏪 Products per Store")
        q = '''
        SELECT s.name as store, COUNT(p.product_id) as product_count,
               AVG(p.price) as avg_price
        FROM product p
        JOIN store s ON p.store_id = s.store_id
        GROUP BY s.name
        ORDER BY product_count DESC
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.bar(df, x='store', y='product_count', color='avg_price',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Price Distribution")
        q = '''
        SELECT price FROM product WHERE price > 0 LIMIT 5000
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.histogram(df, x='price', nbins=50, title="Price Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🔝 Top 10 Best Selling Products")
    q = '''
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
    LIMIT 10
    '''
    df = load_query(q)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ============================================================
# PAGE: ORDER ANALYTICS
# ============================================================
elif page == "🛍️ Order Analytics":
    st.header("🛍️ Order Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_orders = load_query('SELECT COUNT(*) FROM "order"').iloc[0,0]
    total_revenue = load_query('SELECT SUM(total_amount) FROM "order"').iloc[0,0]
    avg_order = load_query('SELECT AVG(total_amount) FROM "order"').iloc[0,0]
    total_items = load_query('SELECT SUM(quantity) FROM order_items').iloc[0,0]
    
    col1.metric("Total Orders", f"{int(total_orders):,}")
    col2.metric("Total Revenue", f"${float(total_revenue or 0):,.2f}")
    col3.metric("Avg Order Value", f"${float(avg_order or 0):,.2f}")
    col4.metric("Total Items Sold", f"{int(total_items or 0):,}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Order Status Distribution")
        q = '''
        SELECT order_status, COUNT(*) as count
        FROM "order"
        GROUP BY order_status
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.pie(df, values='count', names='order_status', hole=0.3)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💳 Revenue by Payment Method")
        q = '''
        SELECT payment_method, SUM(total_amount) as revenue
        FROM "order"
        GROUP BY payment_method
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.bar(df, x='payment_method', y='revenue', color='revenue',
                        color_continuous_scale='Greens')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📈 Monthly Revenue Trend")
    q = '''
    SELECT DATE_TRUNC('month', order_date) as month,
           COUNT(*) as orders,
           SUM(total_amount) as revenue
    FROM "order"
    GROUP BY DATE_TRUNC('month', order_date)
    ORDER BY month
    '''
    df = load_query(q)
    if not df.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['month'], y=df['revenue'], name='Revenue', yaxis='y'))
        fig.add_trace(go.Scatter(x=df['month'], y=df['orders'], name='Orders', yaxis='y2', line=dict(color='red')))
        fig.update_layout(
            yaxis=dict(title='Revenue ($)'),
            yaxis2=dict(title='Orders', overlaying='y', side='right'),
            height=400,
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🔝 Recent Orders")
    q = '''
    SELECT o.order_id, c.name as customer, o.order_date, 
           o.payment_method, o.total_amount, o.order_status
    FROM "order" o
    JOIN customer c ON o.customer_id = c.customer_id
    ORDER BY o.order_date DESC
    LIMIT 20
    '''
    df = load_query(q)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ============================================================
# PAGE: SHIPPING ANALYTICS
# ============================================================
elif page == "🚚 Shipping Analytics":
    st.header("🚚 Shipping Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    total_shipments = load_query('SELECT COUNT(*) FROM shipping').iloc[0,0]
    avg_cost = load_query('SELECT AVG(shipping_cost) FROM shipping').iloc[0,0]
    delivered = load_query("SELECT COUNT(*) FROM shipping WHERE shipping_status = 'Delivered'").iloc[0,0]
    
    col1.metric("Total Shipments", f"{int(total_shipments):,}")
    col2.metric("Avg Shipping Cost", f"${float(avg_cost or 0):.2f}")
    col3.metric("Delivered", f"{int(delivered):,}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Shipping Status Distribution")
        q = '''
        SELECT shipping_status, COUNT(*) as count
        FROM shipping
        GROUP BY shipping_status
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.pie(df, values='count', names='shipping_status',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Shipping Cost Distribution")
        q = '''
        SELECT shipping_cost FROM shipping LIMIT 5000
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.histogram(df, x='shipping_cost', nbins=30,
                              title="Shipping Cost Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🌍 Shipping Analysis by Country")
    q = '''
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
    LIMIT 15
    '''
    df = load_query(q)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ============================================================
# PAGE: REVIEW ANALYTICS
# ============================================================
elif page == "⭐ Review Analytics":
    st.header("⭐ Review Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    total_reviews = load_query('SELECT COUNT(*) FROM product_review').iloc[0,0]
    avg_rating = load_query('SELECT AVG(rating) FROM product_review').iloc[0,0]
    five_star = load_query("SELECT COUNT(*) FROM product_review WHERE rating = 5").iloc[0,0]
    
    col1.metric("Total Reviews", f"{int(total_reviews):,}")
    col2.metric("Average Rating", f"{float(avg_rating or 0):.2f} ⭐")
    col3.metric("5-Star Reviews", f"{int(five_star):,}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⭐ Rating Distribution")
        q = '''
        SELECT rating, COUNT(*) as count
        FROM product_review
        GROUP BY rating
        ORDER BY rating
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.bar(df, x='rating', y='count', color='rating',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 Reviews Over Time")
        q = '''
        SELECT DATE_TRUNC('month', review_date) as month, 
               COUNT(*) as reviews,
               AVG(rating) as avg_rating
        FROM product_review
        WHERE review_date IS NOT NULL
        GROUP BY DATE_TRUNC('month', review_date)
        ORDER BY month
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.line(df, x='month', y='reviews', markers=True)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Average Rating by Category")
    q = '''
    SELECT c.name as category, 
           COUNT(pr.review_id) as total_reviews,
           AVG(pr.rating) as avg_rating
    FROM product_review pr
    JOIN product p ON pr.product_id = p.product_id
    JOIN category c ON p.category_id = c.category_id
    GROUP BY c.name
    ORDER BY avg_rating DESC
    '''
    df = load_query(q)
    if not df.empty:
        fig = px.bar(df, x='category', y='avg_rating', color='total_reviews',
                    title="Average Rating by Category")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🔝 Top Rated Products (Min 5 Reviews)")
    q = '''
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
    LIMIT 10
    '''
    df = load_query(q)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ============================================================
# PAGE: STORE & BRAND ANALYTICS
# ============================================================
elif page == "📊 Store & Brand Analytics":
    st.header("📊 Store & Brand Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏪 Store Performance")
        q = '''
        SELECT s.name as store,
               COUNT(DISTINCT p.product_id) as products,
               SUM(oi.quantity) as items_sold,
               SUM(oi.quantity * oi.unit_price) as revenue
        FROM store s
        JOIN product p ON s.store_id = p.store_id
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY s.name
        ORDER BY revenue DESC
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.bar(df, x='store', y='revenue', color='items_sold',
                        title="Store Revenue", color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Brand Performance")
        q = '''
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
        ORDER BY revenue DESC
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.scatter(df, x='items_sold', y='revenue', size='products',
                            color='avg_rating', hover_name='brand',
                            title="Brand Performance Matrix",
                            color_continuous_scale='RdYlGn')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df, use_container_width=True)

# ============================================================
# PAGE: STOCK MOVEMENT
# ============================================================
elif page == "📈 Stock Movement":
    st.header("📈 Stock Movement Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    total_movements = load_query('SELECT COUNT(*) FROM stock').iloc[0,0]
    total_in = load_query("SELECT SUM(quantity_change) FROM stock WHERE movement_type = 'IN'").iloc[0,0]
    total_out = load_query("SELECT ABS(SUM(quantity_change)) FROM stock WHERE movement_type = 'OUT'").iloc[0,0]
    
    col1.metric("Total Movements", f"{int(total_movements):,}")
    col2.metric("Total Stock In", f"{int(total_in or 0):,}")
    col3.metric("Total Stock Out", f"{int(total_out or 0):,}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Movement Type Distribution")
        q = '''
        SELECT movement_type, COUNT(*) as count,
               SUM(ABS(quantity_change)) as total_quantity
        FROM stock
        GROUP BY movement_type
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.pie(df, values='count', names='movement_type',
                        title="Stock Movement Types")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 Stock Movements Over Time")
        q = '''
        SELECT DATE_TRUNC('month', change_date) as month,
               movement_type,
               SUM(ABS(quantity_change)) as quantity
        FROM stock
        WHERE change_date IS NOT NULL
        GROUP BY DATE_TRUNC('month', change_date), movement_type
        ORDER BY month
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.line(df, x='month', y='quantity', color='movement_type',
                         markers=True, title="Monthly Stock Movements")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📦 Stock Movement by Category")
    q = '''
    SELECT c.name as category, st.movement_type,
           COUNT(*) as movements,
           SUM(ABS(st.quantity_change)) as total_quantity
    FROM stock st
    JOIN product p ON st.product_id = p.product_id
    JOIN category c ON p.category_id = c.category_id
    GROUP BY c.name, st.movement_type
    ORDER BY total_quantity DESC
    '''
    df = load_query(q)
    if not df.empty:
        fig = px.bar(df, x='category', y='total_quantity', color='movement_type',
                    barmode='group', title="Stock Movement by Category")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE: DATA EXPLORER
# ============================================================
elif page == "🔍 Data Explorer":
    st.header("🔍 Data Explorer")
    
    tables = ["country", "store", "category", "brand", "customer", 
              "customer_address", "shipping", "product", '"order"', 
              "order_items", "product_review", "stock"]
    
    selected_table = st.selectbox("Select Table", tables)
    limit = st.slider("Limit rows", 10, 1000, 100)
    
    # Handle reserved keyword
    table_name = selected_table
    
    q = f"SELECT * FROM {table_name} LIMIT {limit}"
    df = load_query(q)
    
    if not df.empty:
        st.subheader(f"Preview: {selected_table.replace('\"', '')}")
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows Shown", len(df))
        with col2:
            total = load_query(f"SELECT COUNT(*) FROM {table_name}").iloc[0,0]
            st.metric("Total Rows", f"{int(total):,}")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, file_name=f"{selected_table.replace('\"', '')}.csv")
    
    st.divider()
    
    st.subheader("🔧 Custom SQL Query")
    custom_query = st.text_area("Enter your SQL query:", height=100,
                                placeholder='SELECT * FROM customer LIMIT 10')
    
    if st.button("Run Query"):
        if custom_query:
            result = load_query(custom_query)
            if not result.empty:
                st.dataframe(result, use_container_width=True)
                st.success(f"Query returned {len(result)} rows")
            else:
                st.warning("Query returned no results")

# Footer
st.divider()
st.caption("📊 E-Commerce Analytics Dashboard | Built with Streamlit & Supabase | 12 Tables Relational Database")
