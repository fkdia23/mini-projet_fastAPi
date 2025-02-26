from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Schémas pour les articles
class ArticleBase(BaseModel):
    title: str
    content: str

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class ArticleInDBBase(ArticleBase):
    id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Article(ArticleInDBBase):
    pass

class ArticleWithAuthor(ArticleInDBBase):
    from app.schemas.user import User
    author: User