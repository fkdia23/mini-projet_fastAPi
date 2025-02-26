from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlmodel import Field, Relationship, SQLModel

class Users(SQLModel, table=True):
    __table_args__ = (
        Index('ix_users_email', 'email', unique=True),
        Index('ix_users_id', 'id'),
        Index('ix_users_username', 'username', unique=True)
    )

    id: Optional[int] = Field(default=None, sa_column=Column('id', Integer, primary_key=True))
    username: Optional[str] = Field(default=None, sa_column=Column('username', String))
    email: Optional[str] = Field(default=None, sa_column=Column('email', String))
    hashed_password: Optional[str] = Field(default=None, sa_column=Column('hashed_password', String))
    is_active: Optional[bool] = Field(default=None, sa_column=Column('is_active', Boolean))
    created_at: Optional[datetime] = Field(default=None, sa_column=Column('created_at', DateTime, server_default=text('CURRENT_TIMESTAMP')))

    articles: List['Articles'] = Relationship(back_populates='author')


class Articles(SQLModel, table=True):
    __table_args__ = (
        Index('ix_articles_id', 'id'),
        Index('ix_articles_title', 'title')
    )

    id: Optional[int] = Field(default=None, sa_column=Column('id', Integer, primary_key=True))
    title: Optional[str] = Field(default=None, sa_column=Column('title', String))
    content: Optional[str] = Field(default=None, sa_column=Column('content', Text))
    author_id: Optional[int] = Field(default=None, sa_column=Column('author_id', ForeignKey('users.id')))
    created_at: Optional[datetime] = Field(default=None, sa_column=Column('created_at', DateTime, server_default=text('CURRENT_TIMESTAMP')))

    author: Optional['Users'] = Relationship(back_populates='articles')
