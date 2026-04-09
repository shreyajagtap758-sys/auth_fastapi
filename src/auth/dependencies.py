
#bearer scheme ka naam, <token> actual token, http reuest me berear token check krta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException
from .utils import decode_token   # utility func, jwt verify krke payload return krta

class tokenbearer(HTTPBearer):

    def __init__(self, auto_error=True):  # auto error is true means we get error when header is not true, if false manual check ki token heyanai
        super().__init__(auto_error=auto_error)   #call init method of httpbearer

    async def __call__(self, request:Request) -> HTTPAuthorizationCredentials | None :
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)

        if not token_data:
            raise HTTPException(
                status_code=403,
                detail="invalid/expired token"
            )

        self.verify_token_data(token_data)

        return token_data
    def verify_token_data(self, token_data):
        raise NotImplementedError("override in child class")

# HTTPBearer + Depends ka combo = clean, reusable dependency jo automatically token provide karega.
class accesstokenbearer(tokenbearer):     #child class of tokenbearer class
    # only checks if user sent access token not refresh token

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
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=403,  # user agar refresh token bheje to error
                detail="please provide an refresh token, not access"
            )