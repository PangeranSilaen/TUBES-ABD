import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import load_query

def render():
    st.markdown('<div class="icon-title"><span class="material-icons">people</span><h2 style="display:inline;">Customer Analytics</h2></div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="icon-title"><span class="material-icons">public</span><h3 style="display:inline;">Top 15 Countries by Customers</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">wc</span><h3 style="display:inline;">Gender Distribution</h3></div>', unsafe_allow_html=True)
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
        
        st.markdown('<div class="icon-title"><span class="material-icons">event</span><h3 style="display:inline;">Customer Signups Over Time</h3></div>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="icon-title"><span class="material-icons">emoji_events</span><h3 style="display:inline;">Top 10 Customers by Total Spending</h3></div>', unsafe_allow_html=True)
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
