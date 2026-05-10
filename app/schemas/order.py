from pydantic import BaseModel
from typing import List,Optional

class OrderItemResponse(BaseModel):
    product_id:int
    product_name_snapshot:str
    price_snapshot:float
    quantity:int
    line_total:float
    class Config:
        from_attributes=True
class OrderResponse(BaseModel):
    id:int
    subtotal_amount:float
    discount_amount:float
    final_amount:float
    coupon_code:Optional[str]
    status:str
    items:List[OrderItemResponse]=[]
    class Config:
        from_attributes=True