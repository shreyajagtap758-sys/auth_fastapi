from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import List



class TagModel(BaseModel):   # reading/returning data
    uid : uuid.UUID
    name : str
    created_at : datetime

    class Config:
        from_attributes = True  # ye orm obejct ko pydantic conver krke route me dega warna orm object use nhi kr sakte=error

class TagCreate(BaseModel):  # create new tags
    name : str

class TagAdd(BaseModel):   # list of tagcreate instances(add multiple tags to a book)
    tags : List[TagCreate]