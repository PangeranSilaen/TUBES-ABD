import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import load_query

def render():
    st.markdown('<div class="icon-title"><span class="material-icons">inventory</span><h2 style="display:inline;">Product Analytics</h2></div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="icon-title"><span class="material-icons">bar_chart</span><h3 style="display:inline;">Products per Category</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">label</span><h3 style="display:inline;">Products per Brand</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">store</span><h3 style="display:inline;">Products per Store</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">attach_money</span><h3 style="display:inline;">Price Distribution</h3></div>', unsafe_allow_html=True)
        q = '''
        SELECT price FROM product WHERE price > 0 LIMIT 5000
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.histogram(df, x='price', nbins=50, title="Price Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="icon-title"><span class="material-icons">trending_up</span><h3 style="display:inline;">Top 10 Best Selling Products</h3></div>', unsafe_allow_html=True)
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
