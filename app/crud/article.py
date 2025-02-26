from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate

def get_article(db: Session, article_id: int) -> Optional[Article]:
    return db.query(Article).filter(Article.id == article_id).first()

def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[Article]:
    return db.query(Article).offset(skip).limit(limit).all()

def get_user_articles(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Article]:
    return db.query(Article).filter(Article.author_id == user_id).offset(skip).limit(limit).all()

def create_article(db: Session, article_create: ArticleCreate, author_id: int) -> Article:
    db_article = Article(
        title=article_create.title,
        content=article_create.content,
        author_id=author_id
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article(db: Session, db_article: Article, article_update: ArticleUpdate) -> Article:
    update_data = article_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_article, field, value)
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def delete_article(db: Session, article_id: int) -> bool:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return False
    
    db.delete(article)
    db.commit()
    return True