import sys,os
from typing import List
from sqlalchemy.orm import Session
from app.models.product import Product
from app.utils.normalization import normalize

# Add cpp_bridge to Python path so we can import trie_module
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","cpp_bridge"))
# pyrefly: ignore [missing-import]
from trie_module import Trie

# Global trie instance (loaded once, lives in memory)
trie=Trie()

def load_trie_from_db(db:Session):
    """Load all active products into the trie on server startup"""
    products=db.query(Product).filter(Product.is_active==True).all()
    for p in products:
        normalized=normalize(p.product_name)
        if normalized:
            trie.insert(normalized)

def sync_trie_insert(product_name:str):
    """Call this when a new product is created"""
    normalized=normalize(product_name)
    if normalized:
        trie.insert(normalized)

def sync_trie_remove(product_name:str):
    """Call this when a product is deleted"""
    normalized=normalize(product_name)
    if normalized:
        trie.remove(normalized)

def autocomplete_products(db:Session,query:str)->List[str]:
    normalized=normalize(query)
    if not normalized:
        return []
    # C++ Trie autocomplete returns normalized names
    results=trie.autocomplete(normalized)
    if not results:
        return []
    # Map normalized names back to actual product names from DB
    products=db.query(Product).filter(Product.normalized_name.in_(results),Product.is_active==True).all()
    return [p.product_name for p in products]

def exact_search_product(db:Session,query:str)->Product|None:
    normalized=normalize(query)
    if not normalized:
        return None
    # Quick C++ Trie check before hitting DB
    if not trie.search(normalized):
        return None
    return db.query(Product).filter(Product.normalized_name==normalized,Product.is_active==True).first()
