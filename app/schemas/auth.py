from __future__ import annotations
import enum
from pydantic import BaseModel
# from pydantic import EmailStr  # install email-validator when online


class UserRole(str,enum.Enum):
    admin="admin"
    user="user"


class UserCreate(BaseModel):
    name:str
    email:str  # use EmailStr when email-validator is installed
    password:str
    # role is always "user" on register


class UserAuth(BaseModel):
    email:str
    password:str


class Token(BaseModel):
    access_token:str
    token_type:str
