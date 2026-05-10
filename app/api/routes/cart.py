from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_active_user
from app.schemas.cart import AddCartItem,UpdateCartItem,CartItemResponse,CartResponse
from app.services import cart_service
from app.services.product_service import get_product_by_id

router=APIRouter()

@router.get("/",response_model=dict)
def get_cart(db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    return cart_service.get_cart_with_details(db,current_user.id)

@router.post("/items",response_model=CartItemResponse)
def add_item(data:AddCartItem,db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    item=cart_service.add_item_to_cart(db,current_user.id,data)
    product=get_product_by_id(db,item.product_id)
    subtotal=product.product_price*item.quantity if product else 0.0
    return {"id":item.id,"product_id":item.product_id,"quantity":item.quantity,"subtotal":subtotal}

@router.put("/items/{item_id}",response_model=CartItemResponse)
def update_item(item_id:int,data:UpdateCartItem,db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    item=cart_service.update_cart_item(db,current_user.id,item_id,data.quantity)
    if not item:
        raise HTTPException(status_code=404,detail="Item not found in cart")
    product=get_product_by_id(db,item.product_id)
    subtotal=product.product_price*item.quantity if product else 0.0
    return {"id":item.id,"product_id":item.product_id,"quantity":item.quantity,"subtotal":subtotal}

@router.delete("/items/{item_id}")
def remove_item(item_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    success=cart_service.remove_cart_item(db,current_user.id,item_id)
    if not success:
        raise HTTPException(status_code=404,detail="Item not found in cart")
    return {"message":"Item removed successfully"}

@router.delete("/")
def clear_cart(db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    cart=cart_service.get_user_cart(db,current_user.id)
    cart_service.clear_cart(db,cart.id)
    return {"message":"Cart cleared successfully"}
