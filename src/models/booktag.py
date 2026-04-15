from sqlmodel import Relationship
from sqlmodel import SQLModel
import uuid
from sqlmodel import Field
from typing import List
from datetime import datetime
from sqlalchemy import Column
import sqlalchemy.dialects.postgresql as pg
import sqlalchemy as sa


class booktaglink(SQLModel, table=True):
    book_uid : uuid.UUID = Field(foreign_key="books.uid", primary_key=True)
    tag_uid : uuid.UUID = Field(foreign_key= "tags.uid", primary_key = True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    uid : uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key = True, nullable = False, default=uuid.uuid4))
    name : str = Field(sa_column=Column(pg.VARCHAR, nullable = False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    books : List["Book"] = Relationship(link_model = booktaglink, back_populates="tags", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"<Tag {self.name}>"
