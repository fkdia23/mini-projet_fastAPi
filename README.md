## Guide de configuration et d'exécution en local

### 1. Préparation de l'environnement

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration de l'environnement

Créez un fichier `.env` à la racine du projet:

```
# Base de données - utilisez SQLite pour les tests locaux
DATABASE_URL=sqlite:///./app.db
# Pour PostgreSQL, utilisez:
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT
SECRET_KEY=votre_cle_secrete_ultra_securisee_a_changer_en_production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Initialisation de la base de données avec Alembic

```bash
# Initialiser le répertoire de migration
alembic init alembic

# Éditer le fichier alembic/env.py pour pointer vers vos modèles
# Ajoutez ces lignes:
# from app.models import Base
# target_metadata = Base.metadata

# Créer votre première migration
alembic revision --autogenerate -m "Initial migration"

# Appliquer la migration
alembic upgrade head
```

### 4. Lancement de l'application

```bash
# Lancer le serveur de développement
uvicorn app.main:app --reload
```

L'API sera disponible à l'adresse http://127.0.0.1:8000

### 5. Documentation automatique

FastAPI génère automatiquement une documentation interactive:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 6. Tests manuels avec l'interface Swagger

1. Ouvrez http://127.0.0.1:8000/docs
2. Inscrivez un utilisateur via `/api/auth/signup`
3. Connectez-vous via `/api/auth/login` pour obtenir un token JWT
4. Cliquez sur le bouton "Authorize" en haut et saisissez votre token
5. Vous pouvez maintenant tester toutes les routes protégées

### 7. Tests avec curl

```bash
# Créer un utilisateur
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/signup' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}'

# Se connecter et récupérer un token
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser&password=password123'

# Utiliser le token pour créer un article
curl -X 'POST' \
  'http://127.0.0.1:8000/api/articles/' \
  -H 'Authorization: Bearer VOTRE_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Mon premier article",
  "content": "Ceci est le contenu de mon premier article."
}'
```

### 8. Tests automatisés (optionnel)

Vous pouvez créer des tests avec `pytest`. Voici un exemple de structure:

```
tests/
  ├── conftest.py    # Fixtures pytest
  ├── test_auth.py   # Tests d'authentification
  ├── test_users.py  # Tests CRUD utilisateurs
  └── test_articles.py  # Tests CRUD articles
```

Et un exemple de commande pour exécuter les tests:

```bash
# Installer pytest
pip install pytest

# Exécuter les tests
pytest
```

### Conseils supplémentaires

1. Pour le développement, SQLite est suffisant mais pour la production, privilégiez PostgreSQL
2. Gardez votre SECRET_KEY confidentielle et changez-la en production
3. Pour les tests en production, envisagez d'ajouter un rate limiting
4. Vérifiez régulièrement les mises à jour de sécurité des dépendances

Cette configuration de base vous permet de tester toutes les fonctionnalités de l'API. N'hésitez pas à personnaliser selon vos besoins spécifiques.

Je vais vous créer une API REST sécurisée avec FastAPI pour gérer des utilisateurs et des articles, en utilisant JWT pour l'authentification. Voici comment je vais structurer le projet:

```plaintext
.
├── alembic/
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── article.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── article.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── article.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── articles.py
│   └── utils/
│       ├── __init__.py
│       └── security.py
├── alembic.ini
├── requirements.txt
├── .env
└── .gitignore

```

Commençons par créer les fichiers essentiels:

```plaintext
fastapi>=0.103.1
uvicorn>=0.23.2
sqlalchemy>=2.0.20
alembic>=1.12.0
pydantic>=2.3.0
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
psycopg2-binary>=2.9.7
python-dotenv>=1.0.0
bcrypt>=4.0.1

```

```python
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "FastAPI User Articles API"
    API_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

settings = Settings()

```

```python
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relation avec les articles
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")

```

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.database import Base

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relation avec l'utilisateur
    author = relationship("User", back_populates="articles")

```

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

```python
from app.models.database import Base, get_db
from app.models.user import User
from app.models.article import Article

__all__ = ["Base", "get_db", "User", "Article"]

```

Maintenant, créons les schémas Pydantic:

```python
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

```

```python
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

```

```python
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

```

```python
from app.schemas.user import User, UserCreate, UserUpdate, UserWithArticles
from app.schemas.article import Article, ArticleCreate, ArticleUpdate, ArticleWithAuthor
from app.schemas.token import Token, TokenPayload

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserWithArticles",
    "Article", "ArticleCreate", "ArticleUpdate", "ArticleWithAuthor",
    "Token", "TokenPayload"
]

```

Maintenant, créons les utilitaires de sécurité:

```python
from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

```

Créons les opérations CRUD:

```python
from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_create: UserCreate) -> User:
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session, db_user: User, user_update: UserUpdate
) -> User:
    update_data = user_update.dict(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

```

```python
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

```

```python
from app.crud.user import (
    get_user, get_user_by_email, get_user_by_username,
    get_users, create_user, update_user, delete_user,
    authenticate_user
)
from app.crud.article import (
    get_article, get_articles, get_user_articles,
    create_article, update_article, delete_article
)

__all__ = [
    "get_user", "get_user_by_email", "get_user_by_username",
    "get_users", "create_user", "update_user", "delete_user",
    "authenticate_user", "get_article", "get_articles", 
    "get_user_articles", "create_article", "update_article", 
    "delete_article"
]

```

Maintenant, créons les dépendances pour les routes protégées:

```python
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.crud.user import get_user
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = get_user(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

```

Maintenant, implémentons les routes API:

```python
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

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
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

```

```python
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.schemas.article import Article
from app.crud.user import get_user, get_users, update_user, delete_user
from app.crud.article import get_user_articles
from app.dependencies import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupère tous les utilisateurs.
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupère un utilisateur par son ID.
    """
    user = get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Met à jour un utilisateur.
    """
    # Vérifier si c'est l'utilisateur courant qui se modifie lui-même
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = update_user(db, db_user=user, user_update=user_in)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Supprime un utilisateur.
    """
    # Vérifier si c'est l'utilisateur courant qui se supprime lui-même
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    delete_user(db, user_id=user_id)


@router.get("/{user_id}/articles", response_model=List[Article])
def read_user_articles(
    user_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupère les articles d'un utilisateur.
    """
    user = get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    articles = get_user_articles(db, user_id=user_id, skip=skip, limit=limit)
    return articles

```

```python
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


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
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

```

```python
from fastapi import APIRouter

from app.api import auth, users, articles

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])

```

Maintenant, créons l'application principale:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.models.database import Base, engine

# Créer les tables dans la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION
)

# Configuration CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclure les routes API
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API User Articles"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

```

Créons la configuration pour Alembic (migrations):

```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# timezone to use when rendering the date
# within the migration file as well as the filename.
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; this defaults
# to alembic/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path
# version_locations = %(here)s/bar %(here
``` 