import enum
from datetime import datetime
from sqlalchemy import Column,Integer,DateTime,Float,String,ForeignKey,Enum
from app.models.base import Base


class OrderStatus(str,enum.Enum):
    placed="placed"
    cancelled="cancelled"
    completed="completed"


class Order(Base):
    __tablename__="orders"
    id=Column(Integer,primary_key=True,index=True,nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    subtotal_amount=Column(Float,nullable=False)
    discount_amount=Column(Float,default=0.0,nullable=False)
    final_amount=Column(Float,nullable=False)
    coupon_code=Column(String,nullable=True)
    status=Column(Enum(OrderStatus),default=OrderStatus.placed,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)
