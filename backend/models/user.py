from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    username: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_premium: bool = False
    projects_count: int = 0
    followers_count: int = 0
    following_count: int = 0

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    username: Optional[str]
    bio: Optional[str]
    avatar: Optional[str]
    is_premium: bool
    projects_count: int
    followers_count: int
    following_count: int

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse