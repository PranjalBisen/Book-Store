from datetime import datetime
from sqlalchemy import Column,Integer,DateTime,ForeignKey
from app.models.base import Base


class Trending(Base):
    __tablename__="trendings"
    product_id=Column(Integer,ForeignKey("products.id"),primary_key=True,nullable=False)
    total_bought=Column(Integer,default=0,nullable=False)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
