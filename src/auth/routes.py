from fastapi import APIRouter, Depends, status
from .schemas import UserCreateModel, UserModel, UserLogicModel
from .service import UserService
from src.db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token, verify_password
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependencies import refreshtokenbearer, accesstokenbearer, get_current_user, rolechecker
from src.db.redis import add_jti_to_blocklist

auth_router = APIRouter() # route for auth file
user_service = UserService()  # userservice() from service file to use here
role_checker = Depends(rolechecker(['admin', "user"]))


REFRESH_TOKEN_EXPIRY=True

@auth_router.post(
    '/signup',
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_Account(
        user_data: UserCreateModel,
        session:AsyncSession = Depends(get_session)
):
    email = user_data.email # see if user already exist using same email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exists")

    new_user = await user_service.create_user(user_data, session)

    return new_user

@auth_router.post('/login')
async def login_users(
        login_data: UserLogicModel, session:AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user  = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.hashed_password)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    "role": user.role
                }
            )
            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

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
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Incorrect email or password",
    )

@auth_router.get('/refresh_token')  # depends(refre..()) calls the __call__ method in refre.. it reads token, decode jwt to token_data, verify refresh token, valid
async def get_new_access(token_detail : dict= Depends(refreshtokenbearer())):
# access expiry of token, if expired then create new access token
    expiry_timestamp = token_detail['exp']  # take token expiry
# refresh token has longer time to get expired like days, within those days user gets the new access toke, else error comes that refresh is expired
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():   # fromtimestamp convert numeric to python object
        new_access_token = create_access_token(  # call to jwt access token for new access token
            user_data=token_detail['user']
        )
        return JSONResponse(content={  #return json to user with new access token
            "access_token": new_access_token
        })

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="expired token") # if token expired, user must login again

@auth_router.get('/me')
async def get_current_user(user = Depends(get_current_user), : bool=Depends(role_checker)):
    return user

@auth_router.get('/logout')
async def revoke_token(token_details: dict=Depends(accesstokenbearer())):

    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message": "logged out successfully"
        },
        status_code=status.HTTP_200_OK
    )
