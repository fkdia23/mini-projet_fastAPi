from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.schemas.user import UserCreate, User
from app.schemas.token import Token
from app.crud.user import authenticate_user, create_user, get_user_by_email, get_user_by_username
from app.utils.security import create_access_token
from app.config import settings

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def create_user_signup(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Crée un nouvel utilisateur.
    """
    # Vérifier si l'email ou le nom d'utilisateur existe déjà
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Créer l'utilisateur
    return create_user(db, user_in)


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Obtenir un JWT pour l'authentification.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }