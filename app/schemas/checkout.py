from pydantic import BaseModel
from typing import Optional,List

class CheckoutCreate(BaseModel):
    discount_code:Optional[str]=None

class CheckoutResponse(BaseModel):
    id:int
    cart_id:int
    discount_code:Optional[str]=None
    total_amount:float
    discount_amount:float=0.0
    final_amount:float
    status:str
    created_at:str
    class Config:
        from_attributes=True