from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str
    email:    EmailStr
    password: str


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"


class RoleOut(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id:         int
    username:   str
    email:      str
    role_id:    int
    role:       Optional[RoleOut] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
