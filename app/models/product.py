from datetime import datetime
from sqlalchemy import Column,Integer,String,DateTime,Float,Boolean,ForeignKey
from app.models.base import Base


class Product(Base):
    __tablename__="products"
    id=Column(Integer,primary_key=True,index=True,nullable=False)
    product_name=Column(String,nullable=False,index=True)
    normalized_name=Column(String,nullable=False,index=True)
    product_description=Column(String,nullable=True)
    product_price=Column(Float,nullable=False)
    product_stock=Column(Integer,nullable=False,default=0)
    category=Column(String,nullable=True)
    is_active=Column(Boolean,default=True,nullable=False)
    created_by=Column(Integer,ForeignKey("users.id"),nullable=True)
    created_at=Column(DateTime,default=datetime.utcnow)
