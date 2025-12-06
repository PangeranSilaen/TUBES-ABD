import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import load_query

def render():
    st.markdown('<div class="icon-title"><span class="material-icons">dashboard</span><h2 style="display:inline;">Overview Dashboard</h2></div>', unsafe_allow_html=True)
    
    # KPI Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_customers = load_query("SELECT COUNT(*) AS cnt FROM customer").iloc[0,0]
    total_orders = load_query('SELECT COUNT(*) AS cnt FROM "order"').iloc[0,0]
    total_revenue = load_query('SELECT COALESCE(SUM(total_amount),0) AS s FROM "order"').iloc[0,0]
    total_products = load_query("SELECT COUNT(*) AS cnt FROM product").iloc[0,0]
    avg_rating = load_query("SELECT AVG(rating) AS a FROM product_review").iloc[0,0]

    col1.metric("Total Customers", f"{int(total_customers):,}")
    col2.metric("Total Orders", f"{int(total_orders):,}")
    col3.metric("Total Revenue", f"${float(total_revenue):,.2f}")
    col4.metric("Total Products", f"{int(total_products):,}")
    col5.metric("Avg Rating", f"{float(avg_rating or 0):.2f} ★")
    
    st.divider()
    
    # Row 2: Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="icon-title"><span class="material-icons">trending_up</span><h3 style="display:inline;">Orders Trend Over Time</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">credit_card</span><h3 style="display:inline;">Payment Method Distribution</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">inventory_2</span><h3 style="display:inline;">Top 10 Categories by Revenue</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">label</span><h3 style="display:inline;">Top 10 Brands by Revenue</h3></div>', unsafe_allow_html=True)
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
