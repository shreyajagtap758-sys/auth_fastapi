import uuid
from pydantic import Field
from pydantic import BaseModel


#create user(signup), usermodel, userlogin
class User(BaseModel):
    uid: uuid.UUID
    user_name: str
    email: str
    password: str = Field(min_length=6)

class user_signup(BaseModel):
    user_name:str=Field(max_length=10)
    email:str
    hashed_password: str = Field(exclude=True)

class user_login(BaseModel):
    email: str
    password : str
