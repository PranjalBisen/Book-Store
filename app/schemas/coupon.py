from pydantic import BaseModel
from typing import Optional

# /////////

class CouponResponse(BaseModel):
    coupon_code:str
    discount_type:str
    coupon_discount:float
    is_active:bool
    class Config:
        from_attributes=True
