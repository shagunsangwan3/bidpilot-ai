import bcrypt
from jose import jwt
from datetime import datetime, timedelta
import os

# NOTE: previously hardcoded as "super-secret-key-change-later" directly in source
# control. Falls back to that only for local dev; set JWT_SECRET_KEY in the real
# environment before deploying anywhere real users can reach.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-later")
ALGORITHM = "HS256"

# CRITICAL: previously used passlib's CryptContext(schemes=["bcrypt"]). passlib
# 1.7.4 (pinned in requirements.txt) hasn't been updated since 2020 and its bcrypt
# backend does a version-detection self-test on first use that assumes an
# `__about__` attribute bcrypt removed in 4.1+. With bcrypt==5.0.0 (also pinned in
# requirements.txt), that self-test itself throws
# "ValueError: password cannot be longer than 72 bytes" — meaning hash_password()
# crashed on every single call, so registration and login were completely broken.
# This is a known, widely-reported passlib/bcrypt incompatibility, not anything
# specific to this codebase. Calling bcrypt directly sidesteps passlib's detection
# code entirely. bcrypt's hash format ($2b$...) is unchanged either way, so every
# password hash already stored in the database remains valid — no data migration
# needed for this fix.
BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(truncated, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    truncated = password.encode("utf-8")[:BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(truncated, hashed.encode("utf-8"))

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