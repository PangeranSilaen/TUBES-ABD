"""
Data Explorer page - Advanced SQL query editor with validation
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from config import TABLES
from utils import load_query, validate_sql_query, format_sql, execute_query_safe

def render():
    """Render Data Explorer page"""
    st.markdown('<div class="icon-title"><span class="material-icons">search</span><h2 style="display:inline;">Data Explorer</h2></div>', unsafe_allow_html=True)
    
    # Initialize session state for query history
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    # Tabs for different modes
    tab1, tab2, tab3 = st.tabs([
        "Quick Table View",
        "Advanced SQL Editor", 
        "Query History"
    ])
    
    # ========================================
    # TAB 1: Quick Table View
    # ========================================
    with tab1:
        st.markdown('<div class="icon-title"><span class="material-icons">table_chart</span><h3 style="display:inline;">Quick Table Preview</h3></div>', unsafe_allow_html=True)
        
        tables = TABLES + ['"order"']  # Add order with quotes for SQL
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_table = st.selectbox("Select Table", tables, key="quick_table")
        with col2:
            limit = st.slider("Limit rows", 10, 1000, 100, key="quick_limit")
        
        if st.button("Load Table", key="load_quick"):
            table_name = selected_table
            q = f"SELECT * FROM {table_name} LIMIT {limit}"
            df = load_query(q)
            
            if not df.empty:
                st.markdown(f"#### Preview: `{selected_table.replace('\"', '')}`")
                st.dataframe(df, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows Shown", len(df))
                with col2:
                    total = load_query(f"SELECT COUNT(*) FROM {table_name}").iloc[0,0]
                    st.metric("Total Rows", f"{int(total):,}")
                with col3:
                    st.metric("Columns", len(df.columns))
                
                # Download options
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{selected_table.replace('\"', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_quick"
                )
    
    # ========================================
    # TAB 2: Advanced SQL Editor
    # ========================================
    with tab2:
        st.markdown('<div class="icon-title"><span class="material-icons">code</span><h3 style="display:inline;">Advanced SQL Query Editor</h3></div>', unsafe_allow_html=True)
        st.caption("⚡ Supports complex queries: JOINs, CTEs, subqueries, window functions, aggregations, and more")
        
        # Example queries dropdown
        example_queries = {
            "Simple SELECT": "SELECT * FROM customer LIMIT 10",
            "JOIN Multiple Tables": """SELECT 
    c.name AS customer_name,
    co.name AS country,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM customer c
JOIN country co ON c.country_id = co.country_id
LEFT JOIN "order" o ON c.customer_id = o.customer_id
GROUP BY c.name, co.name
ORDER BY total_spent DESC
LIMIT 20""",
            "Complex Aggregation with CASE": """SELECT 
    c.name AS category,
    COUNT(DISTINCT p.product_id) AS total_products,
    AVG(p.price) AS avg_price,
    SUM(CASE WHEN p.price > 100 THEN 1 ELSE 0 END) AS premium_products,
    SUM(CASE WHEN p.price <= 50 THEN 1 ELSE 0 END) AS budget_products
FROM product p
JOIN category c ON p.category_id = c.category_id
GROUP BY c.name
ORDER BY total_products DESC""",
            "CTE (Common Table Expression)": """WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS revenue,
        COUNT(*) AS orders
    FROM "order"
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT 
    month,
    revenue,
    orders,
    revenue / orders AS avg_order_value,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    revenue - LAG(revenue) OVER (ORDER BY month) AS revenue_change
FROM monthly_sales
ORDER BY month DESC""",
            "Subquery with Window Function": """SELECT 
    p.name AS product,
    c.name AS category,
    p.price,
    AVG(p.price) OVER (PARTITION BY c.category_id) AS category_avg_price,
    p.price - AVG(p.price) OVER (PARTITION BY c.category_id) AS price_diff_from_avg,
    RANK() OVER (PARTITION BY c.category_id ORDER BY p.price DESC) AS price_rank_in_category
FROM product p
JOIN category c ON p.category_id = c.category_id
WHERE p.price > (SELECT AVG(price) FROM product)
ORDER BY c.name, price_rank_in_category""",
            "Top Customers by Category": """SELECT 
    c.name AS customer,
    cat.name AS category,
    SUM(oi.quantity) AS items_bought,
    SUM(oi.quantity * oi.unit_price) AS spent
FROM customer c
JOIN "order" o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN product p ON oi.product_id = p.product_id
JOIN category cat ON p.category_id = cat.category_id
GROUP BY c.name, cat.name
HAVING SUM(oi.quantity * oi.unit_price) > 1000
ORDER BY spent DESC
LIMIT 50""",
            "Reviews with Product Details": """SELECT 
    pr.review_id,
    p.name AS product,
    c.name AS category,
    b.name AS brand,
    pr.rating,
    pr.review_date,
    AVG(pr.rating) OVER (PARTITION BY p.product_id) AS product_avg_rating,
    COUNT(*) OVER (PARTITION BY p.product_id) AS product_review_count
FROM product_review pr
JOIN product p ON pr.product_id = p.product_id
JOIN category c ON p.category_id = c.category_id
JOIN brand b ON p.brand_id = b.brand_id
WHERE pr.rating >= 4
ORDER BY pr.review_date DESC
LIMIT 100"""
        }
        
        selected_example = st.selectbox(
            "Load Example Query",
            ["-- Select an example --"] + list(example_queries.keys()),
            key="example_selector"
        )
        
        if st.button("Load Example", key="load_example"):
            if selected_example != "-- Select an example --":
                st.session_state.custom_query = example_queries[selected_example]
                st.rerun()
        
        # SQL Query Input
        if 'custom_query' not in st.session_state:
            st.session_state.custom_query = "SELECT * FROM customer LIMIT 10"
        
        custom_query = st.text_area(
            "SQL Query",
            value=st.session_state.custom_query,
            height=250,
            help="Enter any SQL query. Complex queries with JOINs, CTEs, subqueries are supported.",
            key="sql_input"
        )
        
        # Update session state
        st.session_state.custom_query = custom_query
        
        # Query controls
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        
        with col1:
            run_query = st.button("Run Query", type="primary", key="run_sql")
        with col2:
            format_query = st.button("Format SQL", key="format_sql")
        with col3:
            validate_only = st.button("Validate", key="validate_sql")
        with col4:
            clear_query = st.button("Clear", key="clear_sql")
        
        # Format SQL
        if format_query:
            try:
                formatted = format_sql(custom_query)
                st.session_state.custom_query = formatted
                st.success("✓ Query formatted!")
                st.rerun()
            except Exception as e:
                st.error(f"Could not format query: {e}")
        
        # Clear query
        if clear_query:
            st.session_state.custom_query = ""
            st.rerun()
        
        # Validate query
        if validate_only:
            is_safe, query_type, warning = validate_sql_query(custom_query)
            if is_safe:
                st.success(f"✓ Query is valid. Type: {query_type or 'SELECT'}")
                if warning:
                    st.warning(warning)
            else:
                st.error(warning or "Query validation failed")
        
        # Run query
        if run_query and custom_query:
            # Validate first
            is_safe, query_type, warning = validate_sql_query(custom_query)
            
            if not is_safe:
                st.error(warning or "Query blocked for safety")
            else:
                # Show warning for write operations
                if warning:
                    st.warning(warning)
                    confirm = st.checkbox(f"I understand this {query_type} will modify data", key="confirm_write")
                    if not confirm:
                        st.stop()
                
                # Execute query
                with st.spinner("Executing query..."):
                    start_time = datetime.now()
                    result, error = execute_query_safe(custom_query)
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    if error:
                        st.error(error)
                    elif result is not None:
                        # Save to history
                        st.session_state.query_history.insert(0, {
                            'query': custom_query,
                            'timestamp': datetime.now(),
                            'rows': len(result),
                            'execution_time': execution_time,
                            'type': query_type
                        })
                        
                        # Keep only last 50 queries
                        if len(st.session_state.query_history) > 50:
                            st.session_state.query_history = st.session_state.query_history[:50]
                        
                        # Display results
                        st.success(f"✓ Query executed successfully in {execution_time:.3f}s")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows Returned", len(result))
                        with col2:
                            st.metric("Columns", len(result.columns) if not result.empty else 0)
                        with col3:
                            st.metric("Execution Time", f"{execution_time:.3f}s")
                        
                        if not result.empty:
                            st.dataframe(result, use_container_width=True, height=400)
                            
                            # Download options
                            csv = result.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Download Results",
                                data=csv,
                                file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key="download_result"
                            )
                        else:
                            st.info("Query executed but returned no rows")
        
        # Query info panel
        with st.expander("Query Guidelines & Security"):
            st.markdown("""
            **Supported Operations:**
            - ✅ **SELECT** - All types (simple, JOINs, CTEs, subqueries, window functions)
            - ✅ **INSERT** - Add new data (with confirmation)
            - ✅ **UPDATE** - Modify existing data (with confirmation)
            - ✅ **DELETE** - Remove data (with confirmation)
            - ❌ **CREATE/DROP/ALTER/TRUNCATE** - Blocked for safety
            
            **Advanced Features Supported:**
            - 🔗 **Complex JOINs** - INNER, LEFT, RIGHT, FULL OUTER, CROSS
            - 📊 **Aggregations** - GROUP BY, HAVING, COUNT, SUM, AVG, MIN, MAX
            - 🪟 **Window Functions** - ROW_NUMBER, RANK, LAG, LEAD, PARTITION BY
            - 🔄 **CTEs** - WITH clauses, recursive CTEs
            - 🎯 **Subqueries** - Correlated and non-correlated
            - 🔢 **CASE Expressions** - Complex conditional logic
            - 📅 **Date Functions** - DATE_TRUNC, EXTRACT, date arithmetic
            - 🔤 **String Functions** - CONCAT, SUBSTRING, LOWER, UPPER, etc.
            
            **Tips:**
            - Use `LIMIT` to preview large result sets
            - Format your query for better readability
            - Test complex queries with `Validate Only` first
            - Use example queries as templates
            """)
    
    # ========================================
    # TAB 3: Query History
    # ========================================
    with tab3:
        st.markdown('<div class="icon-title"><span class="material-icons">history</span><h3 style="display:inline;">Query Execution History</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.query_history:
            st.caption(f"Showing {len(st.session_state.query_history)} recent queries")
            
            for idx, entry in enumerate(st.session_state.query_history):
                with st.expander(
                    f"{idx+1}. {entry['type'] or 'SELECT'} - {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} "
                    f"({entry['rows']} rows, {entry['execution_time']:.3f}s)"
                ):
                    st.code(entry['query'], language='sql')
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button("Re-run Query", key=f"rerun_{idx}"):
                            st.session_state.custom_query = entry['query']
                            st.rerun()
                    with col2:
                        if st.button("Copy to Editor", key=f"copy_{idx}"):
                            st.session_state.custom_query = entry['query']
                            st.success("Copied to editor!")
                            st.rerun()
            
            if st.button("Clear History", key="clear_history"):
                st.session_state.query_history = []
                st.rerun()
        else:
            st.info("No query history yet. Run some queries in the Advanced SQL Editor tab!")
