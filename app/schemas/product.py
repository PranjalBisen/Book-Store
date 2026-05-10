from typing import Optional
from pydantic import BaseModel

class ProductCreate(BaseModel):
    product_name:str
    product_description:Optional[str]=None
    product_price:float
    product_stock:int
    category:Optional[str]=None

class ProductUpdate(BaseModel):
    product_name:Optional[str]=None
    product_description:Optional[str]=None
    product_price:Optional[float]=None
    product_stock:Optional[int]=None
    category:Optional[str]=None
    is_active:Optional[bool]=None

class StockUpdate(BaseModel):
    product_stock:int

class ProductResponse(BaseModel):
    id:int
    product_name:str
    product_description:Optional[str]
    product_price:float
    product_stock:int
    category:Optional[str]
    is_active:bool
    availability:str
    class Config:
        from_attributes=True
