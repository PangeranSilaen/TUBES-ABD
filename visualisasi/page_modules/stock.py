import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import load_query

def render():
    st.markdown('<div class="icon-title"><span class="material-icons">move_to_inbox</span><h2 style="display:inline;">Stock Movement Analytics</h2></div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="icon-title"><span class="material-icons">donut_large</span><h3 style="display:inline;">Movement Type Distribution</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">date_range</span><h3 style="display:inline;">Stock Movements Over Time</h3></div>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="icon-title"><span class="material-icons">category</span><h3 style="display:inline;">Stock Movement by Category</h3></div>', unsafe_allow_html=True)
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
