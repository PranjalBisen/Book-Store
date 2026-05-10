from pydantic import BaseModel









class TrendingResponse(BaseModel):
    product_id:int
    total_bought:int
    product_name:str
    class Config:
        from_attributes=True
