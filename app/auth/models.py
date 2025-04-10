from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str
    division: str
    whatsappNumber: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    division: Optional[str] = None
    whatsappNumber: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None


class User(UserBase):
    id: str
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
