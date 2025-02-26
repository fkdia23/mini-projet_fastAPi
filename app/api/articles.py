from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.article import Article, ArticleCreate, ArticleUpdate
from app.crud.article import get_article, get_articles, create_article, update_article, delete_article
from app.dependencies import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Article])
def read_articles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupère tous les articles.
    """
    articles = get_articles(db, skip=skip, limit=limit)
    return articles


@router.get("/{article_id}", response_model=Article)
def read_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupère un article par son ID.
    """
    article = get_article(db, article_id=article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    return article


@router.post("/", response_model=Article, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Crée un nouvel article.
    """
    article = create_article(db, article_in, author_id=current_user.id)
    return article


@router.put("/{article_id}", response_model=Article)
def update_article_endpoint(
    article_id: int,
    article_in: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Met à jour un article.
    """
    article = get_article(db, article_id=article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Vérifier si l'utilisateur courant est l'auteur de l'article
    if article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    article = update_article(db, db_article=article, article_update=article_in)
    return article


# @router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Supprime un article.
    """
    article = get_article(db, article_id=article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Vérifier si l'utilisateur courant est l'auteur de l'article
    if article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    delete_article(db, article_id=article_id)