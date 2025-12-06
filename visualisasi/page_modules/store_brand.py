import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import load_query

def render():
    st.markdown('<div class="icon-title"><span class="material-icons">analytics</span><h2 style="display:inline;">Store & Brand Analytics</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="icon-title"><span class="material-icons">storefront</span><h3 style="display:inline;">Store Performance</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">local_offer</span><h3 style="display:inline;">Brand Performance</h3></div>', unsafe_allow_html=True)
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
