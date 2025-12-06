"""Page modules package initialization - imports all page modules"""
from . import overview
from . import customer
from . import product
from . import order
from . import shipping
from . import review
from . import store_brand
from . import stock
from . import data_explorer

__all__ = [
    'overview',
    'customer',
    'product',
    'order',
    'shipping',
    'review',
    'store_brand',
    'stock',
    'data_explorer'
]
