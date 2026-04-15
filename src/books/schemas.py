from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List
from src.reviews.schemas import reviewmodel
from src.tags.schemas import TagModel


class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None
    price: float
    pages: int
    language: str
    rating: float


class BookUpdate(BaseModel):
     title: str | None = None
     author: str | None = None
     description: str | None = None
     price: float | None = None
     rating: float | None = None
     pages: int | None = None
     language: str | None = None
     is_available: bool | None = None

class BookRead(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    description:str
    price: float
    created_at: datetime
    rating: float | None = None
    pages: int | None = None
    language: str | None = None
    is_available: bool | None = None
    tags: list[TagModel] = []

class BookDetailModel(BookRead):
    reviews: List[reviewmodel]

