# generate pass hash, verify pass hash , access, refresh token
import logging
import uuid
from datetime import timedelta, datetime
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from src.config import Config

passw_hash = CryptContext(scheme=['argon2'])
ACCESS_TOKEN_EXPIRY = 3600

def create_pass_hash(password: str):
    return passw_hash.hash(password)

def verify_pass_hash(password: str, hash: str):
    return passw_hash.verify(password, hash)

def create_access_token(user : dict, expiry : timedelta = None, refresh : bool = False):
    payload = {}

    payload['user'] = user.user_name
    payload['email'] = user.email
    payload['exp'] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )  # expiry user se a sakti he
    payload['jti'] = str(uuid.uuid4())  #jwt need string uuid to store
    payload['refresh'] = refresh

    token = jwt.encode(
        payload,
        key = Config.JWT_SECRET,
        algorithm = Config.JWT_ALGORITHM
    ) # here we dont use list because we are assigning algo
    return token

def decode_token(token: str) -> dict: #Turn a random string into a trusted identity you can use to make decisions
    try:
        token_get = jwt.decode(
            token,
            key = Config.JWT_SECRET,
            algorithms = [Config.JWT_ALGORITHM]  # library expects list
        ) # here algo take list because, this verify algo, meaning there can be multiple algo so use list
        return token_get

    except ExpiredSignatureError:  # ye ya fir
        logging.exception("Token expired")

    except JWTError:  # ye
        logging.exception("Invalid token")
