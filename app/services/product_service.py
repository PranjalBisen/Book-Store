from typing import List,Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate,ProductUpdate,StockUpdate
from app.utils.normalization import normalize
from fastapi import HTTPException


def create_product(db:Session,data:ProductCreate,admin_id:int)->Product:
    normalized=normalize(data.product_name)
    product=Product(
        product_name=data.product_name,
        product_description=data.product_description,
        product_price=data.product_price,
        product_stock=data.product_stock,
        category=data.category,
        created_by=admin_id,
        normalized_name=normalized
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_products(db:Session,limit:int=20,offset:int=0)->List[Product]:
    return db.query(Product).offset(offset).limit(limit).all()

def get_product_by_id(db:Session,product_id:int)->Product|None:
    return db.query(Product).filter(Product.id==product_id).first() 

def get_product_by_name(db:Session,product_name:str)->Product|None:
    normalized=normalize(product_name)
    return db.query(Product).filter(Product.normalized_name==normalized).first()

def update_product(db:Session,product_id:int,data:ProductUpdate)->Optional[Product]:
    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        return None
    
    update_data=data.model_dump(exclude_unset=True)
    if "product_name" in update_data and update_data["product_name"]:
        product.normalized_name=normalize(update_data["product_name"])
    for key,value in update_data.items():
        setattr(product,key,value)
    db.commit()
    db.refresh(product)
    return product

def delete_product(db:Session,product_id:int)->bool:
    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        return False
    product.is_active=False
    db.commit()
    return True

def update_stock(db:Session,product_id:int,data:StockUpdate)->Optional[Product]:
    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        return None
    product.product_stock=data.product_stock
    db.commit()
    db.refresh(product)
    return product
