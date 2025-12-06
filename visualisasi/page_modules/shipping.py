import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import load_query

def render():
    st.markdown('<div class="icon-title"><span class="material-icons">local_shipping</span><h2 style="display:inline;">Shipping Analytics</h2></div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="icon-title"><span class="material-icons">donut_small</span><h3 style="display:inline;">Shipping Status Distribution</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">account_balance_wallet</span><h3 style="display:inline;">Shipping Cost Distribution</h3></div>', unsafe_allow_html=True)
        q = '''
        SELECT shipping_cost FROM shipping LIMIT 5000
        '''
        df = load_query(q)
        if not df.empty:
            fig = px.histogram(df, x='shipping_cost', nbins=30,
                              title="Shipping Cost Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="icon-title"><span class="material-icons">language</span><h3 style="display:inline;">Shipping Analysis by Country</h3></div>', unsafe_allow_html=True)
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
