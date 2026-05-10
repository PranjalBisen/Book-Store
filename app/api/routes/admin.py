from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.deps import require_admin
from app.schemas.product import ProductCreate,ProductUpdate,StockUpdate,ProductResponse
from app.services import product_service

router=APIRouter()

@router.post("/products",response_model=ProductResponse)
def create_product(data:ProductCreate,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    return product_service.create_product(db,data,current_user.id)

@router.put("/products/{product_id}",response_model=ProductResponse)
def update_product(product_id:int,data:ProductUpdate,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    product=product_service.update_product(db,product_id,data)
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    success=product_service.delete_product(db,product_id)
    if not success:
        raise HTTPException(status_code=404,detail="Product not found")
    return {"message":"Product deleted successfully"}

@router.patch("/products/{product_id}/stock",response_model=ProductResponse)
def update_stock(product_id:int,data:StockUpdate,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    product=product_service.update_stock(db,product_id,data)
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    return product
