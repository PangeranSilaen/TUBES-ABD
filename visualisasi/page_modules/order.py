import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import load_query

def render():
    st.markdown('<div class="icon-title"><span class="material-icons">shopping_bag</span><h2 style="display:inline;">Order Analytics</h2></div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="icon-title"><span class="material-icons">pie_chart</span><h3 style="display:inline;">Order Status Distribution</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">payment</span><h3 style="display:inline;">Revenue by Payment Method</h3></div>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="icon-title"><span class="material-icons">timeline</span><h3 style="display:inline;">Monthly Revenue Trend</h3></div>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="icon-title"><span class="material-icons">history</span><h3 style="display:inline;">Recent Orders</h3></div>', unsafe_allow_html=True)
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
