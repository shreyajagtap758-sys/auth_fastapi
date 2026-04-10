import datetime
from datetime import timedelta

from fastapi import FastAPI, APIRouter, Depends
from starlette.responses import JSONResponse

from auth.dependencies import refreshtokenbearer, accesstokenbearer
from db.redis import add_jti_to_blocklist
from ownauth.service import user_service, user_signup
from src.db.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from ownauth.schema import User, user_login
from fastapi.exceptions import HTTPException
from ownauth.utils import verify_pass_hash, create_pass_hash, create_access_token, create_refresh_token

user_router = APIRouter()
service_user = user_service()

REFRESH_TOKEN_EXP = 2 #days

@user_router.post('/user', response_model=user_signup)
async def create_user(user_data: User, session: AsyncSession = Depends(get_session)):
    user_email = user_data.email
    user = await service_user.users_email(user_email, session)

    if user:
        raise HTTPException(
            detail= "user already exists"
        )

    new_user = await service_user.user_create(user_data, session)
    return new_user

@user_router.post('/login_user')
async def login(user_data : user_login, session: AsyncSession= Depends(get_session)):
    email = user_data.email
    passw = user_data.password
    user = await service_user.users_email(email, session)

    # verify given pass and hashed pass stored in db
    if user is not None:
        valid_pass = verify_pass_hash(passw, user.hashed_password)

        if valid_pass:
            access_token = create_access_token(
                {'email': user_data.email,
                 'user_id': str(user.uid)
                 })
            refresh_token = create_refresh_token({
                'email': user.email,
                'user_id': str(user.uid)
            })
            refresh = True
            expiry= timedelta(days=REFRESH_TOKEN_EXP)

            return JSONResponse(
                content={
                    "message": "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
    raise HTTPException(
        detail="incorrect email/password"
    )

@user_router.get('/get_refresh')
async def get_new_access(token_detail: dict = Depends(refreshtokenbearer())):
    # ensure this is a refresh token
    if not token_detail.get("refresh"):
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    new_access = create_access_token(user_data=token_detail['user'])

    return JSONResponse(
        content={
            "access_token": new_access
        }
    )
    # if token invalid,user gets messg, if token expired= this jwt checks on its own, no mana expiry check

@user_router.get('/logout')
async def logout_user(token_detail: dict=Depends(accesstokenbearer())):
    jti = token_detail['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        {"message" : "logged out successfully"},
        status_code = 200  #ok
    )
