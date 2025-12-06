"""
E-Commerce Analytics Dashboard - Main Application
Modular structure with separated page components
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, PAGE_LAYOUT, CUSTOM_CSS, TABLES, engine
from page_modules import overview, customer, product, order, shipping, review, store_brand, stock, data_explorer

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    layout=PAGE_LAYOUT,
    page_icon=APP_ICON
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Main title
st.markdown(
    '<div class="icon-title"><span class="material-icons">shopping_cart</span>'
    '<h1 style="display:inline;">E-Commerce Analytics Dashboard</h1></div>',
    unsafe_allow_html=True
)
st.caption("Visualisasi Data dari 12 Tabel Relasional - Synthetic E-Commerce Dataset")

# Check database connection
if engine is None:
    st.error("DATABASE_URL belum diset. Silakan copy `.env.example` ke `.env` dan isi `DATABASE_URL`.")
    st.stop()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown(
        '<div style="text-align: center;">'
        '<span class="material-icons" style="font-size: 64px; color: #4CAF50;">shopping_cart</span>'
        '</div>',
        unsafe_allow_html=True
    )
    st.header("Dashboard Navigation")
    
    page = st.selectbox("Pilih Halaman", [
        "Overview Dashboard",
        "Customer Analytics",
        "Product Analytics",
        "Order Analytics",
        "Shipping Analytics",
        "Review Analytics",
        "Store & Brand Analytics",
        "Stock Movement",
        "Data Explorer"
    ])
    
    st.divider()
    st.markdown("### Database Tables")
    for t in TABLES:
        st.markdown(f"- `{t}`")

# ============================================================
# PAGE ROUTING
# ============================================================
if page == "Overview Dashboard":
    overview.render()
elif page == "Customer Analytics":
    customer.render()
elif page == "Product Analytics":
    product.render()
elif page == "Order Analytics":
    order.render()
elif page == "Shipping Analytics":
    shipping.render()
elif page == "Review Analytics":
    review.render()
elif page == "Store & Brand Analytics":
    store_brand.render()
elif page == "Stock Movement":
    stock.render()
elif page == "Data Explorer":
    data_explorer.render()

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("E-Commerce Analytics Dashboard | Built with Streamlit & Supabase | 12 Tables Relational Database")
