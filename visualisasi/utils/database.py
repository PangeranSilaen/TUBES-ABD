"""
Database query utilities
"""
import streamlit as st
import pandas as pd
from config import engine

@st.cache_data(ttl=300)
def load_query(q):
    """Execute SQL query and return DataFrame with caching"""
    try:
        return pd.read_sql_query(q, engine)
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()
