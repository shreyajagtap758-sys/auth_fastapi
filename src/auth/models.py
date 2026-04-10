import uuid
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column


class User(SQLModel, table=True):
    _tablename_= 'users'
    uid : uuid.UUID = Field(
            default_factory=uuid.uuid4,
            nullable=False,
            primary_key=True

    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=True, server_default="user"
    ))
    is_verified: bool = Field(default=False)
    hashed_password: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))


    def _repr_(self):
        return f'<User {self.username}>'