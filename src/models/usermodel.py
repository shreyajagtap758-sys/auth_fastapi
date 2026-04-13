import uuid
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy as sa
from typing import List


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, default=uuid.uuid4, primary_key=True, nullable=False))
    username: str
    email: str
    first_name: str
    last_name: str

    role: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=True, server_default="user"
    ))
    # with back populate: we are linking relationship, without it the two tables won't know abt each other
    # use lazy: selectin so we fetch all book together in one query, otherwise (lazy=select)//default we would have to send one query per book, it would increase queries
    books: List["Book"] = Relationship(back_populates="user",
                                              sa_relationship_kwargs={'lazy': 'selectin'})
    # create foreign key-> join with primary key->backpopulates,relationship -> lazy=selectin
    # this is one(user) to many(books) relationship
    # we use  sa_relationship_kwargs={'lazy':'selectin'} because sqlmodel cant handle this pure orm(it combines pydantic+sqlalchemy), so by using sa_relationship kwars we tell to directly sqlalchemy to use advanced options (laxy etc) through sqmodel
    # we are use sqlmodel here as base not sqlalchemy in model, so we have to use it, else if we have pure sqlalchemy model we can directly use laxy options
    reviews: List["Review"] = Relationship(back_populates="user",
                                       sa_relationship_kwargs={'lazy': 'selectin'})

    is_verified: bool = Field(default=False)
    hashed_password: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=sa.text("now()")))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=sa.text("now()")))

    def _repr_(self):
        return f'<User {self.username}>'
