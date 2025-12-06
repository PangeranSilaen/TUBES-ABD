"""
Configuration and database connection setup
Supports both Streamlit secrets (deployment) and .env (local)
"""
import os
import streamlit as st
from sqlalchemy import create_engine

# Database URL - prioritize Streamlit secrets for deployment
try:
    DATABASE_URL = st.secrets["DATABASE_URL"]
except (FileNotFoundError, KeyError):
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine(url):
    """Create SQLAlchemy engine with proper SSL configuration"""
    if not url:
        return None
    return create_engine(url, connect_args={"sslmode": "require"})

engine = get_engine(DATABASE_URL)

# App configuration
APP_TITLE = "E-Commerce Analytics Dashboard"
APP_ICON = "📊"
PAGE_LAYOUT = "wide"

# Custom CSS with Material Icons
CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
<style>
    .metric-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
    }
    .icon-title {
        display: inline-flex;
        align-items: center;
        gap: 10px;
    }
    .icon-title .material-icons,
    .icon-title .material-symbols-outlined {
        font-size: 32px;
        vertical-align: middle;
    }
    .sidebar-icon {
        vertical-align: middle;
        margin-right: 8px;
        font-size: 20px;
    }
</style>
"""

# Database tables
TABLES = [
    "country", "store", "category", "brand", "customer", 
    "customer_address", "shipping", "product", "order", 
    "order_items", "product_review", "stock"
]
