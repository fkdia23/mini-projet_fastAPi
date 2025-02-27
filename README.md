# mini-projet_fastAPi
Je vais vous créer une API REST sécurisée avec FastAPI pour gérer des utilisateurs et des articles, en utilisant JWT pour l'authentification. Voici comment je vais structurer le projet:
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

Guide de configuration et d'exécution en local
1. Préparation de l'environnement
'''
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
'''

2. Configuration de l'environnement
Créez un fichier .env à la racine du projet:
'''
# Base de données - utilisez SQLite pour les tests locaux
DATABASE_URL=sqlite:///./app.db
# Pour PostgreSQL, utilisez:
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT
SECRET_KEY=votre_cle_secrete_ultra_securisee_a_changer_en_production
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''

3. Initialisation de la base de données avec Alembic

'''
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
'''

4. Lancement de l'application

'''
# Lancer le serveur de développement
uvicorn app.main:app --reload
'''

L'API sera disponible à l'adresse http://127.0.0.1:8000
5. Documentation automatique
FastAPI génère automatiquement une documentation interactive:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

6. Tests manuels avec l'interface Swagger

Ouvrez http://127.0.0.1:8000/docs
Inscrivez un utilisateur via /api/auth/signup
Connectez-vous via /api/auth/login pour obtenir un token JWT
Cliquez sur le bouton "Authorize" en haut et saisissez votre token
Vous pouvez maintenant tester toutes les routes protégées


7. Tests avec curl
bashCopy# Créer un utilisateur
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
8. Tests automatisés (optionnel)
Vous pouvez créer des tests avec pytest. Voici un exemple de structure:
Copytests/
  ├── conftest.py    # Fixtures pytest
  ├── test_auth.py   # Tests d'authentification
  ├── test_users.py  # Tests CRUD utilisateurs
  └── test_articles.py  # Tests CRUD articles
Et un exemple de commande pour exécuter les tests:
bashCopy# Installer pytest
pip install pytest

# Exécuter les tests
pytest
Conseils supplémentaires

Pour le développement, SQLite est suffisant mais pour la production, privilégiez PostgreSQL
Gardez votre SECRET_KEY confidentielle et changez-la en production
Pour les tests en production, envisagez d'ajouter un rate limiting
Vérifiez régulièrement les mises à jour de sécurité des dépendances

Cette configuration de base vous permet de tester toutes les fonctionnalités de l'API. N'hésitez pas à personnaliser selon vos besoins spécifiques.