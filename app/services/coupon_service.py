from typing import Optional
from sqlalchemy.orm import Session
from app.models.coupon import Coupon,DiscountType

def get_coupon_by_code(db:Session,code:str)->Optional[Coupon]:
    if not code:
        return None
    return db.query(Coupon).filter(Coupon.coupon_code==code,Coupon.is_active==True).first()

def calculate_discount(coupon:Coupon,subtotal:float)->float:
    if not coupon:
        return 0.0
    if coupon.discount_type==DiscountType.percent:
        discount=(coupon.coupon_discount/100.0)*subtotal
        return min(discount,subtotal)
    elif coupon.discount_type==DiscountType.flat:
        return min(coupon.coupon_discount,subtotal)
    return 0.0
