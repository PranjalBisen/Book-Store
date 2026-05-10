from typing import List
from pydantic import BaseModel
from typing import Optional,List

class AddCartItem(BaseModel):
    product_id:int
    quantity:int

class UpdateCartItem(BaseModel):
    quantity:int

class CartItemResponse(BaseModel):
    id:int
    product_id:int
    quantity:int
    subtotal:float
    class Config:
        from_attributes=True

class CartResponse(BaseModel):
    id:int
    items:List[CartItemResponse]
    total_amount:float
    discount_amount:float=0.0
    final_amount:float
    class Config:
        from_attributes=True