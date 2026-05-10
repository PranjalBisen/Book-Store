import enum
from datetime import datetime
from sqlalchemy import Column,Integer,String,DateTime,Boolean,Enum
from app.models.base import Base


class UserRole(str,enum.Enum):
    admin="admin"
    user="user"


class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True,nullable=False)
    name=Column(String,nullable=False)
    email=Column(String,unique=True,index=True,nullable=False)
    hashed_password=Column(String,nullable=False)
    role=Column(Enum(UserRole),default=UserRole.user,nullable=False)
    is_active=Column(Boolean,default=True,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)
