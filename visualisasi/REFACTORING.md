# Refactored App Structure

## Overview
Dashboard telah di-refactor dari **1152 lines** monolithic file menjadi **modular structure** yang clean dan maintainable.

## New Structure

```
visualisasi/
├── app.py                      # Main entry (80 lines) ✨
├── config.py                   # Configuration (57 lines)
├── requirements.txt            # Dependencies
├── .env                        # Environment variables
├── ICON_USAGE.md              # Icon & SQL editor docs
├── README.md                   # Original README
│
├── utils/                      # Utility modules
│   ├── __init__.py            # Package init
│   ├── database.py            # DB query functions (14 lines)
│   └── validators.py          # SQL validation (68 lines)
│
└── pages/                      # Page modules (644 lines total)
    ├── __init__.py            # Package init (21 lines)
    ├── overview.py            # Overview Dashboard (97 lines)
    ├── customer.py            # Customer Analytics (81 lines)
    ├── product.py             # Product Analytics (103 lines)
    ├── order.py               # Order Analytics (84 lines)
    ├── shipping.py            # Shipping Analytics (64 lines)
    ├── review.py              # Review Analytics (88 lines)
    ├── store_brand.py         # Store & Brand (56 lines)
    ├── stock.py               # Stock Movement (71 lines)
    └── data_explorer.py       # Data Explorer (345 lines) ⭐
```

## Before vs After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Main app.py** | 1,152 lines | 80 lines | **93% reduction** |
| **Files** | 1 monolithic | 13 modular | Better organization |
| **Readability** | Low | High | ✅ |
| **Maintainability** | Hard | Easy | ✅ |
| **Reusability** | No | Yes | ✅ |

## Key Changes

### 1. **config.py** - Centralized Configuration
```python
# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = get_engine(DATABASE_URL)

# App settings
APP_TITLE = "E-Commerce Analytics Dashboard"
CUSTOM_CSS = """..."""  # Material Icons CSS
TABLES = ["country", "store", ...]
```

### 2. **utils/** - Reusable Utilities

**database.py:**
```python
@st.cache_data(ttl=300)
def load_query(q):
    # Cached query execution
```

**validators.py:**
```python
def validate_sql_query(query):
    # SQL validation with sqlparse
def execute_query_safe(query):
    # Safe query execution
```

### 3. **pages/** - Modular Pages

Each page has a `render()` function:
```python
def render():
    st.markdown('<div class="icon-title">...</div>')
    # Page logic here
```

### 4. **app.py** - Clean Routing
```python
# Simple page routing
if page == "Overview Dashboard":
    overview.render()
elif page == "Customer Analytics":
    customer.render()
# ... etc
```

## Benefits

### ✅ **Maintainability**
- Each page is independent
- Easy to find and edit specific features
- Clear separation of concerns

### ✅ **Scalability**
- Add new pages by creating new file in `pages/`
- Shared utilities in `utils/` prevent duplication
- Easy to add new features without breaking existing code

### ✅ **Readability**
- Main `app.py` is now 80 lines (vs 1152)
- Each page file is focused on single responsibility
- No need to scroll 1000+ lines to find code

### ✅ **Testing**
- Can test individual pages in isolation
- Utilities can be unit tested separately
- Easier to debug issues

### ✅ **Collaboration**
- Multiple developers can work on different pages
- Less merge conflicts
- Clear file ownership

## Migration Notes

### Old Code Location → New Location

| Feature | Old | New |
|---------|-----|-----|
| DB Connection | app.py line 20 | config.py |
| SQL Queries | app.py scattered | utils/database.py |
| SQL Validation | app.py line 77-135 | utils/validators.py |
| Overview Page | app.py line 170-256 | pages/overview.py |
| Customer Page | app.py line 262-340 | pages/customer.py |
| Product Page | app.py line 346-448 | pages/product.py |
| Order Page | app.py line 454-538 | pages/order.py |
| Shipping Page | app.py line 544-608 | pages/shipping.py |
| Review Page | app.py line 614-701 | pages/review.py |
| Store/Brand Page | app.py line 707-762 | pages/store_brand.py |
| Stock Page | app.py line 768-809 | pages/stock.py |
| Data Explorer | app.py line 815-1145 | pages/data_explorer.py |

## Icon Fixes in Data Explorer

All emoji replaced with Material Icons:
- ✅ `📋` → `<span class="material-icons">table_chart</span>`
- ✅ `💻` → Already clean
- ✅ `📜` → `<span class="material-icons">history</span>`
- ✅ `📥` → Added `icon="📥"` to buttons (Streamlit native)
- ✅ `🔄` → Added `icon="🔄"` to buttons
- ✅ `📋` → Added `icon="📋"` to buttons
- ✅ `🗑️` → Added `icon="🗑️"` to buttons

## How to Run

```bash
cd visualisasi
streamlit run app.py
```

Everything works exactly the same, just organized better! 🎉

## Adding New Pages

1. Create new file in `pages/`, e.g., `pages/analytics.py`
2. Add `render()` function with page logic
3. Import in `pages/__init__.py`
4. Add route in `app.py`:
   ```python
   elif page == "New Analytics":
       analytics.render()
   ```

## Backup

Original monolithic app saved as `app_old.py` (1152 lines).
