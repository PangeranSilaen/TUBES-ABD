# Icon Library Usage in Dashboard

## Overview
Dashboard ini menggunakan **Google Material Icons** untuk tampilan yang lebih profesional dan less "AI-generated".

---

## Advanced SQL Query Editor

### Overview
Dashboard dilengkapi dengan **Advanced SQL Query Editor** yang mendukung query DML kompleks, bukan hanya simple SELECT.

### Features

#### ✅ Supported SQL Operations

**Read Operations (Safe, No Confirmation)**
- `SELECT` - All variations supported:
  - Simple SELECT
  - Multi-table JOINs (INNER, LEFT, RIGHT, FULL OUTER, CROSS)
  - Subqueries (correlated & non-correlated)
  - Common Table Expressions (CTEs) with WITH clause
  - Window Functions (ROW_NUMBER, RANK, LAG, LEAD, PARTITION BY)
  - Complex aggregations (GROUP BY, HAVING)
  - CASE expressions
  - Date/Time functions (DATE_TRUNC, EXTRACT, etc.)

**Write Operations (Require Confirmation)**
- `INSERT` - Add new records
- `UPDATE` - Modify existing records
- `DELETE` - Remove records

**Blocked Operations (Security)**
- ❌ `CREATE` - Table/index creation blocked
- ❌ `DROP` - Destructive operations blocked
- ❌ `ALTER` - Schema modifications blocked
- ❌ `TRUNCATE` - Mass deletion blocked

#### 🛠️ Built-in Tools

1. **SQL Formatter**
   - Auto-indent and beautify SQL
   - Uppercase keywords
   - Preserve comments

2. **Query Validator**
   - Parse SQL before execution
   - Check for dangerous operations
   - Show query type

3. **Example Queries**
   - 7 pre-built complex query templates
   - JOINs, CTEs, window functions, aggregations
   - One-click load to editor

4. **Query History**
   - Last 50 queries saved
   - Execution time tracking
   - Re-run or copy previous queries
   - Clear history option

5. **Export Results**
   - Download query results as CSV
   - Timestamped filenames

### Implementation Details

**Library Used:** `sqlparse`
- Industry-standard SQL parser
- Handles complex SQL syntax
- Safe query type detection

**Installation:**
```bash
pip install sqlparse
```

**Security Validation:**
```python
def validate_sql_query(query):
    # Parse SQL
    parsed = sqlparse.parse(query)
    stmt = parsed[0]
    query_type = stmt.get_type()
    
    # Block dangerous DDL
    if query_type in ['CREATE', 'DROP', 'ALTER', 'TRUNCATE']:
        return False
    
    # Warn on DML writes
    if query_type in ['INSERT', 'UPDATE', 'DELETE']:
        return True, warning
    
    # Allow SELECT
    return True
```

### Usage Examples

#### Example 1: Complex JOIN with Aggregation
```sql
SELECT 
    c.name AS customer_name,
    co.name AS country,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM customer c
JOIN country co ON c.country_id = co.country_id
LEFT JOIN "order" o ON c.customer_id = o.customer_id
GROUP BY c.name, co.name
ORDER BY total_spent DESC
LIMIT 20
```

#### Example 2: CTE with Window Function
```sql
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS revenue
    FROM "order"
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month,
    revenue - LAG(revenue) OVER (ORDER BY month) AS growth
FROM monthly_sales
ORDER BY month DESC
```

#### Example 3: Subquery with CASE
```sql
SELECT 
    c.name AS category,
    COUNT(DISTINCT p.product_id) AS total_products,
    SUM(CASE WHEN p.price > 100 THEN 1 ELSE 0 END) AS premium,
    SUM(CASE WHEN p.price <= 50 THEN 1 ELSE 0 END) AS budget
FROM product p
JOIN category c ON p.category_id = c.category_id
GROUP BY c.name
ORDER BY total_products DESC
```

### Query Editor UI

**3 Tabs:**
1. **Quick Table View** - Browse tables quickly
2. **Advanced SQL Editor** - Full SQL capabilities
3. **Query History** - Review past queries

**Controls:**
- ▶️ **Run Query** - Execute SQL
- ✨ **Format SQL** - Auto-beautify
- ✓ **Validate Only** - Check syntax without running
- 🗑️ **Clear** - Reset editor

**Metrics Displayed:**
- Rows returned
- Columns count
- Execution time (seconds)

### Why This Approach?

**Alternative 1: No validation (❌ Rejected)**
- Pros: Simple
- Cons: Dangerous, can DROP tables

**Alternative 2: Regex-based parsing (❌ Rejected)**
- Pros: No dependencies
- Cons: Breaks on complex SQL (CTEs, nested queries)

**Alternative 3: sqlparse library (✅ Chosen)**
- Pros: Industry-standard, handles complex SQL
- Cons: Small dependency (200KB)

**Alternative 4: sqlalchemy inspection only (❌ Rejected)**
- Pros: Already used for DB connection
- Cons: Not a parser, can't detect query type

### Future Enhancements

- [ ] Syntax highlighting with Ace Editor
- [ ] Query autocomplete
- [ ] Visual query builder
- [ ] Explain/Analyze query plans
- [ ] Query performance profiling
- [ ] Save favorite queries
- [ ] Share queries via URL

---

## Material Icons Implementation

### Material Icons
- **Library**: Google Material Icons (Material Symbols)
- **CDN**: Loaded via Google Fonts CDN
- **No extra package installation required**

```html
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
```

### Icon Usage Pattern

```python
st.markdown('<div class="icon-title"><span class="material-icons">icon_name</span><h2 style="display:inline;">Title Text</h2></div>', unsafe_allow_html=True)
```

## Icon Mapping (Emoji → Material Icons)

| Section | Old (Emoji) | New (Material Icon) |
|---------|-------------|---------------------|
| Dashboard | 🛒 | `shopping_cart` |
| Overview | 📊 | `dashboard` |
| Customers | 👥 | `people` |
| Products | 📦 | `inventory` |
| Orders | 🛍️ | `shopping_bag` |
| Shipping | 🚚 | `local_shipping` |
| Reviews | ⭐ | `star_rate` |
| Analytics | 📊 | `analytics` |
| Stock | 📈 | `move_to_inbox` |
| Explorer | 🔍 | `search` |
| Trending | 📈 | `trending_up` |
| Payment | 💳 | `credit_card` / `payment` |
| Countries | 🌍 | `public` / `language` |
| Store | 🏪 | `storefront` / `store` |
| Brand | 🏷️ | `label` / `local_offer` |
| Money | 💰 | `attach_money` / `account_balance_wallet` |

## Alternatives Considered

### 1. **streamlit-extras** (Not used)
```bash
pip install streamlit-extras
```
```python
from streamlit_extras.colored_header import colored_header
```
- Pros: Native Streamlit integration
- Cons: Requires extra package, limited icon set

### 2. **Font Awesome** (Not used)
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```
- Pros: Huge icon library
- Cons: Larger bundle size, commercial restrictions

### 3. **Bootstrap Icons** (Not used)
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
```
- Pros: Clean design, good selection
- Cons: Less comprehensive than Material

## Why Material Icons?

✅ **No installation required** - CDN-based  
✅ **Official Google design** - Professional and consistent  
✅ **Comprehensive library** - 2000+ icons  
✅ **Free & open source** - Apache License 2.0  
✅ **Web-standard** - Optimized for web rendering  
✅ **Well-documented** - Easy to find icon names  

## Icon Browser

Browse available icons:
- https://fonts.google.com/icons
- https://material.io/resources/icons/

## Custom Styling

Icons styled via CSS in `app.py`:

```css
.icon-title {
    display: inline-flex;
    align-items: center;
    gap: 10px;
}
.icon-title .material-icons {
    font-size: 32px;
    vertical-align: middle;
}
```

## Future Enhancements

- Add hover effects to icons
- Implement icon color themes
- Add animated icons for loading states
- Custom SVG icons for specific metrics
