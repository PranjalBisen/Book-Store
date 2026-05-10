from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import UserCreate,TokenResponse
from app.models.user import User
from app.services import auth_service
from app.core.security import create_access_token
from app.api.deps import get_current_active_user

router=APIRouter()

@router.post("/register",response_model=dict)
def register(user_in:UserCreate,db:Session=Depends(get_db)):
    user=auth_service.register_user(db,user_in)
    return {"message":"User created successfully","user_id":user.id}

@router.post("/login",response_model=TokenResponse)
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=auth_service.authenticate_user(db,form_data.username,form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token=create_access_token(subject=user.id)
    return {"access_token":access_token,"token_type":"bearer"}

@router.get("/me",response_model=dict)
def read_users_me(current_user:User=Depends(get_current_active_user)):
    return {
        "id":current_user.id,
        "name":current_user.name,
        "email":current_user.email,
        "role":current_user.role
    }
