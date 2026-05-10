from typing import List
from sqlalchemy.orm import Session
from app.models.trending import Trending
from app.models.product import Product

def update_trending(db:Session,product_id:int,product_name:str,quantity_bought:int)->Trending:
    trending=db.query(Trending).filter(Trending.product_id==product_id).first()
    if trending:
        trending.total_bought+=quantity_bought
    else:
        trending=Trending(
            product_id=product_id,
            product_name=product_name,
            total_bought=quantity_bought
        )
        db.add(trending)    
    # We do not commit here because this is called inside the checkout transaction
    return trending

def get_top_trending(db:Session,limit:int=10)->List[Trending]:
    return db.query(Trending).order_by(Trending.total_bought.desc()).limit(limit).all()
