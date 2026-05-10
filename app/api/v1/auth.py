from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.login import Login
from app.core import security

router=APIRouter()

@router.post("/login")
async def login(credentials:Login,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==credentials.username).first()
    if not user or not security.verify_password(credentials.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token=security.create_access_token(subject=user.id)
    return {"access_token":access_token,"token_type":"bearer"}

@router.post("/register")
async def register(credentials:Login,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==credentials.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    new_user=User(
        username=credentials.username,
        hashed_password=security.get_password_hash(credentials.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"User created successfully","username":new_user.username}