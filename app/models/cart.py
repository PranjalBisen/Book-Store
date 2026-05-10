from datetime import datetime
from sqlalchemy import Column,Integer,DateTime,Boolean,ForeignKey
from app.models.base import Base


class Cart(Base):
    __tablename__="carts"
    id=Column(Integer,primary_key=True,index=True,nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"),unique=True,nullable=False)
    is_active=Column(Boolean,default=True,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)