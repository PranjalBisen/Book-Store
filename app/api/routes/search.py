from typing import List
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.product import ProductResponse
from app.services import search_service

router=APIRouter()

@router.get("/autocomplete",response_model=List[str])
def autocomplete(q:str,db:Session=Depends(get_db)):
    return search_service.autocomplete_products(db,q)

@router.get("/exact",response_model=ProductResponse)
def exact_search(q:str,db:Session=Depends(get_db)):
    product=search_service.exact_search_product(db,q)
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    product.availability="in_stock" if product.product_stock>0 else "out_of_stock"
    return product
