from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# Schémas pour l'utilisateur
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserWithArticles(UserInDBBase):
    from app.schemas.article import Article
    articles: List[Article] = []