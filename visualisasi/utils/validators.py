"""
SQL query validation and formatting utilities
"""
import sqlparse
from sqlalchemy import text
import pandas as pd
from config import engine

def validate_sql_query(query):
    """
    Validate SQL query for safety and return parsed info
    Returns: (is_safe, query_type, warning_message)
    """
    if not query or not query.strip():
        return False, None, "Query is empty"
    
    # Parse SQL
    parsed = sqlparse.parse(query)
    if not parsed:
        return False, None, "Invalid SQL syntax"
    
    stmt = parsed[0]
    query_type = stmt.get_type()
    
    # DDL operations (CREATE, DROP, ALTER, TRUNCATE) - BLOCKED
    dangerous_ddl = ['CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'RENAME']
    if query_type in dangerous_ddl:
        return False, query_type, f"❌ {query_type} operations are blocked for safety"
    
    # DML operations that modify data - WARNING but allowed
    write_operations = ['INSERT', 'UPDATE', 'DELETE']
    if query_type in write_operations:
        return True, query_type, f"⚠️ Warning: {query_type} will modify data in the database"
    
    # SELECT and other read operations - SAFE
    return True, query_type, None

def format_sql(query):
    """Format SQL query for better readability"""
    return sqlparse.format(
        query, 
        reindent=True, 
        keyword_case='upper',
        strip_comments=False
    )

def execute_query_safe(query):
    """Execute query with proper error handling and logging"""
    try:
        from sqlalchemy import text
        
        # For SELECT queries, use read_sql_query
        is_safe, query_type, warning = validate_sql_query(query)
        
        if not is_safe:
            return None, warning
        
        # Execute query
        if query_type in ['INSERT', 'UPDATE', 'DELETE']:
            # For write operations, use execute
            with engine.connect() as conn:
                result = conn.execute(text(query))
                conn.commit()
                return pd.DataFrame({'affected_rows': [result.rowcount]}), None
        else:
            # For SELECT
            df = pd.read_sql_query(query, engine)
            return df, None
            
    except Exception as e:
        return None, f"❌ Error: {str(e)}"
