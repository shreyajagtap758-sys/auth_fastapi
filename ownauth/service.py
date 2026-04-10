from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from ownauth.schema import user_signup
from src.db.database import get_session
from ownauth.model import Usermodel
from sqlalchemy import select


class user_service:

    async def users_email(self, email: str, session : AsyncSession):
        statement = select(Usermodel).where(Usermodel.email == email)  # database mese ye lene keliye session use

        result = await session.execute(statement)
        user =  result.scalar_one_or_none()
        return user is not None

    async def user_create(self, user : user_signup, session : AsyncSession):

        user_dict = user.model_dump()
        new_user = Usermodel(
            **user_dict
        )
        # hashed pass generate
        new_user.hashed_password = generate_passwd_hash(user_dict['password'])

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user
