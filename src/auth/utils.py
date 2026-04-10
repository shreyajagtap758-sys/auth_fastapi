from passlib.context import CryptContext  # password hash algorithm manager
from datetime import datetime, timedelta  # timedelta= duration used for expiry token
from src.config import Config
from jose import jwt, JWTError, ExpiredSignatureError

import uuid
import logging

passwd_context = CryptContext(schemes=["argon2"])  #argon2 is hashing algorithm using cryptcontext manager

ACCESS_TOKEN_EXPIRES = 3600 # token expiry 3600 seconds= 1 hour


def generate_passwd_hash(password: str) -> str:
    return passwd_context.hash(password)
# password leke, hash generate(salt=each hashed pass is diff for all users)

def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)
# password, hash leke, verify dono= output=true/false

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}  # data jo token me jayega jwt me ye teen hota or unko banana hota{header, payload, signature}
# access token= user already login he, isme user ata as dict, expiry:timedelta none mtlab expiery he lekin default(1 hour or anything) set,or refresh = false mtlab ye access token he not refresh token
    payload['user'] = user_data  # user data jayega
    payload['exp'] = datetime.now() + (   #expiry data jisme abi ka datetime + expiry default else if none toh timedelta, jo access token expire banaya tha wo use
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRES)
    )
    payload['jti'] = str(uuid.uuid4()) # jti=hwt id= har token ka uniue identifier, uuid.uuid4 generate uniue random string, and str(uuid) object ko str convert krke jwt me store

    payload['refresh'] = refresh  # token type= true = refresh token, false=acces token.access token api call krta, refresh token new access token geenrate
   # refresh me humne false store kiya tha
    token = jwt.encode(  # jwt me payload,header(algo), secret(signature) hota
        payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
    )

    return token # encode token create- client send


def decode_token(token: str) -> dict:  #ab client decoded token ko bhejega, ab usko encode
    try:
        token_data = jwt.decode(  # token ko verify kro db me stored jwt secret or algo ke sath
            token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
        )

        return token_data    #toke valid- dict return(dict me whi key jo encode me thi)

    except ExpiredSignatureError:  # ye ya fir
        logging.exception("Token expired")

    except JWTError:  # ye
        logging.exception("Invalid token")