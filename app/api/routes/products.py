from typing import List
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.product import ProductResponse
from app.services import product_service

router=APIRouter()

@router.get("/",response_model=List[ProductResponse])
def get_products(skip:int=0,limit:int=100,db:Session=Depends(get_db)):
    products=product_service.get_products(db,skip,limit)
    # Map the computed field availability for the response
    for p in products:
        p.availability="in_stock" if p.product_stock>0 else "out_of_stock"
    return products

@router.get("/{product_id}",response_model=ProductResponse)
def get_product(product_id:int,db:Session=Depends(get_db)):
    product=product_service.get_product(db,product_id)
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    product.availability="in_stock" if product.product_stock>0 else "out_of_stock"
    return product
