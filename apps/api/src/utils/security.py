from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

# NOTE: previously hardcoded as "super-secret-key-change-later" directly in source
# control. Falls back to that only for local dev; set JWT_SECRET_KEY in the real
# environment before deploying anywhere real users can reach.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-later")
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=1)

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )