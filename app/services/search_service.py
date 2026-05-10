from typing import List
from sqlalchemy.orm import Session
from app.models.product import Product
from app.utils.normalization import normalize

def autocomplete_products(db:Session,query:str)->List[str]:
    # Trie will comehere
    normalized=normalize(query)
    if not normalized:
        return []
    # Dummy DB implementation until Trie is ready
    products=db.query(Product).filter(Product.normalized_name.startswith(normalized),Product.is_active==True).limit(10).all()
    return [p.product_name for p in products]

def exact_search_product(db:Session,query:str)->Product|None:
    # Trie will come here
    normalized=normalize(query)
    if not normalized:
        return None
    return db.query(Product).filter(Product.normalized_name==normalized,Product.is_active==True).first()
