
#bearer scheme ka naam, <token> actual token, http reuest me berear token check krta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, Depends
from .utils import decode_token   # utility func, jwt verify krke payload return krta
from src.db.redis import token_in_blockedlist
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.database import get_session
from .service import UserService
from typing import List, Any
from src.models import User

user_service = UserService()

class tokenbearer(HTTPBearer):
# class tokenbearer ko oject ki tar use krne init kiya ,fir uss object ko runkrne call kiya
    def __init__(self, auto_error=True):  # auto error is true means we get error when header is not true, if false manual check ki token heyanai
        super().__init__(auto_error=auto_error)   #call init method of httpbearer

    async def __call__(self, request:Request) -> HTTPAuthorizationCredentials | None :
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)

        token = creds.credentials.strip()

        if " " in token:
            print("⚠️ Token contains spaces:", token)

        if token.count(".") != 2:
            print("❌ Invalid JWT format:", token)

        if not token_data:
            raise HTTPException(
                status_code=403,
                detail={"error" : "invalid/expired token",
                        "resolution": "get new access token"}
            )

        if await token_in_blockedlist(token_data['jti']):
            raise HTTPException(
                status_code=403,
                detail={"error" : "invalid token/revoked",
                "resolution": "please get new token"}
            )

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError("override in child class")

# HTTPBearer + Depends ka combo = clean, reusable dependency jo automatically token provide karega.
class accesstokenbearer(tokenbearer):     #child class of tokenbearer class
    # only checks if user sent access token ,not refresh token

    def verify_token_data(self, token_data: dict) -> None:
        # if token data(not none) and token data is refresh_token = error
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=403,  # user agar refresh token bheje to error
                detail="please provide an access token, not refresh"
            )

class refreshtokenbearer(tokenbearer):  # child class of token bearer
    def verify_token_data(self, token_data: dict) -> None:
        # if token data(not none) and token data is NOT refresh_token = error
        if token_data and token_data['access']:
            raise HTTPException(
                status_code=403,  # user agar refresh token bheje to error
                detail="please provide an refresh token, not access"
            )

async def get_current_user(
    token_details: dict=Depends(accesstokenbearer()),
    session: AsyncSession= Depends(get_session)
):
    user_email = token_details["user"]["email"]

    user = await user_service.get_user_by_email(user_email, session)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

class rolechecker:
    def __init__(self, allowed_roles: List[str]) -> None:

        self.allowed_roles = allowed_roles
 # get user from db + token verify from get current user
    async def __call__(self, current_user: User= Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code=403,
            detail="you are not allowed to perform this action"
        )
