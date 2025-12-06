import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import load_query

def render():
    st.markdown('<div class="icon-title"><span class="material-icons">star_rate</span><h2 style="display:inline;">Review Analytics</h2></div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="icon-title"><span class="material-icons">star</span><h3 style="display:inline;">Rating Distribution</h3></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="icon-title"><span class="material-icons">calendar_today</span><h3 style="display:inline;">Reviews Over Time</h3></div>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="icon-title"><span class="material-icons">assessment</span><h3 style="display:inline;">Average Rating by Category</h3></div>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="icon-title"><span class="material-icons">grade</span><h3 style="display:inline;">Top Rated Products (Min 5 Reviews)</h3></div>', unsafe_allow_html=True)
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
