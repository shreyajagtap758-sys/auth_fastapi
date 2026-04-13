from pydantic import BaseModel, Field
from src.books.schemas import BookRead
import uuid
from datetime import datetime
from typing import List
from src.reviews.schemas import reviewmodel


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=10)
    email: str = Field(max_length=40)
    password: str = Field(min_length=7, max_length=72)

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    hashed_password: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime

class UserBooks(BaseModel):
    user : UserModel  # we can now use user.books
    books: List[BookRead]   # books.user
    reviews : List[reviewmodel]

class UserLogicModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=7, max_length=72)