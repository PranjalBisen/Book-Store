from sqlalchemy import Column,Integer,Float,String,ForeignKey
from app.models.base import Base


class OrderItem(Base):
    __tablename__="order_items"
    id=Column(Integer,primary_key=True,index=True,nullable=False)
    order_id=Column(Integer,ForeignKey("orders.id"),nullable=False)
    product_id=Column(Integer,ForeignKey("products.id"),nullable=False)
    product_name_snapshot=Column(String,nullable=False)
    price_snapshot=Column(Float,nullable=False)
    quantity=Column(Integer,nullable=False)
    line_total=Column(Float,nullable=False)
