from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_active_user
from app.schemas.checkout import CheckoutCreate,CheckoutResponse
from app.services import checkout_service

router=APIRouter()

@router.post("/",response_model=CheckoutResponse)
def checkout(data:CheckoutCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    order=checkout_service.process_checkout(db,current_user.id,data)
    return {
        "id":order.id,
        "cart_id":0, # Cart is deleted/cleared in db, just putting 0 for the schema
        "discount_code":order.coupon_code,
        "total_amount":order.subtotal_amount,
        "discount_amount":order.discount_amount,
        "final_amount":order.final_amount,
        "status":order.status,
        "created_at":str(order.created_at)
    }
