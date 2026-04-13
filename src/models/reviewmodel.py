import uuid
from typing import Optional, List
import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, default=uuid.uuid4, primary_key=True, nullable=False))

    rating : int = Field(lt=5)
    review_text : str

    book_uid: Optional[uuid.UUID] = Field(foreign_key="books.uid", nullable=False) # tablename = books, uid column
    user_uid : Optional[uuid.UUID] = Field(foreign_key="users.uid", nullable=False)

    user : Optional["User"] = Relationship(back_populates="reviews")
    book : Optional["Book"] = Relationship(back_populates="reviews")

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,server_default=sa.text("now()")))  # default handle by server_default db, sa.text is war sl= returning postgres function now(time)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=sa.text("now()")))

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}"