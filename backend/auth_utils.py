# backend/auth_utils.py
import os
import time
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
load_dotenv()

PWD_CTX = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", "86400"))  # default 1 day

def hash_password(password: str) -> str:
    return PWD_CTX.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return PWD_CTX.verify(password, password_hash)

def create_jwt_token(username: str) -> str:
    payload = {
        "sub": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP_SECONDS
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # pyjwt v2 returns str
    return token

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None
