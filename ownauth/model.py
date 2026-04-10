import uuid
from enum import unique

from pydantic import Field
from sqlalchemy import Column, Integer, Float, String
from sqlmodel import SQLModel

# usermodel db,

class Usermodel(SQLModel, table=True):
    __tablename__ = "user_handle"

    uid : uuid.UUID = Field(Column(primary_key=True, Nullable=False,default_factory=uuid.uuid4))
    user_name : str
    email : str = Field(Column(unique = True, index = True, Nullable=False))
    hashed_password: str = Field(Column(exclude=True, Nullale=False))

    def __refer__(self):
        return f'<Usermodel {self.user_name}>'