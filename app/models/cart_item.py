from datetime import datetime
from sqlalchemy import Column,Integer,DateTime,ForeignKey,UniqueConstraint
from app.models.base import Base


class CartItem(Base):
    __tablename__="cart_items"
    id=Column(Integer,primary_key=True,index=True,nullable=False)
    cart_id=Column(Integer,ForeignKey("carts.id"),nullable=False)
    product_id=Column(Integer,ForeignKey("products.id"),nullable=False)
    quantity=Column(Integer,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)
    __table_args__=(UniqueConstraint("cart_id","product_id"),)
