import enum
from sqlalchemy import Column,Integer,Float,String,Boolean,Enum
from app.models.base import Base


class DiscountType(str,enum.Enum):
    percent="percent"
    flat="flat"


class Coupon(Base):
    __tablename__="coupons"
    id=Column(Integer,primary_key=True,index=True,nullable=False)
    coupon_code=Column(String,unique=True,index=True,nullable=False)
    discount_type=Column(Enum(DiscountType),nullable=False)
    coupon_discount=Column(Float,nullable=False)
    is_active=Column(Boolean,default=True,nullable=False)
