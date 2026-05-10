from sqlalchemy.orm import Session
from app.models.user import User,UserRole
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password,create_access_token
from fastapi import HTTPException

def register_user(db:Session,data:UserCreate)->User:
    exist=db.query(User).filter(User.email==data.email).first()
    if exist:
        raise HTTPException(status_code=400,detail="User already exists")
    hashed=get_password_hash(data.password)
    user=User(
        name=data.name,
        email=data.email,
        hashed_password=hashed,
        role=UserRole.user
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db:Session,email:str,password:str)->User|None:
    user=db.query(User).filter(User.email==email).first()
    if not user or not verify_password(password,user.hashed_password):
        return None
    return user
    