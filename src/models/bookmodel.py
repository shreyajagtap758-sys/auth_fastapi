from sqlmodel import SQLModel, Field, Column, Relationship
import uuid
from datetime import datetime
from typing import Optional, List
import sqlalchemy.dialects.postgresql as pg
import sqlalchemy as sa
from src.models import booktaglink


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(default=uuid.uuid4, primary_key=True, nullable=False)

    title: str
    author: str
    description: str | None = None
    user_uid : Optional[uuid.UUID] = Field(foreign_key="users.uid", nullable=False) #users is the auth model table name,we r pointing to uid
    price: float
    rating: float
    pages: int

    user : Optional["User"] = Relationship(back_populates="books")  # who submitted a book, for that we fetch user's data from user table
    reviews: List["Review"] = Relationship(back_populates="book",
                                           sa_relationship_kwargs={'lazy': 'selectin'})
    tags: List["Tag"] = Relationship(
        back_populates="books",
        link_model=booktaglink
    )

    language: str
    is_available: bool = True

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,server_default=sa.text("now()")))  # default handle by server_default db, sa.text is war sl= returning postgres function now(time)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=sa.text("now()")))



