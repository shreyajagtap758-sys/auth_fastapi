from pydantic import BaseModel, Field
import uuid
from typing import Optional
from datetime import datetime


class reviewmodel(BaseModel):
    uid: uuid.UUID
    rating: int = Field(le=5)
    review_text: str
    book_uid: Optional[uuid.UUID]
    user_uid: Optional[uuid.UUID]

    created_at: datetime

    updated_at: datetime


class reviewcreatemodel(BaseModel):
    rating: int = Field(le=5)
    review_text: str
