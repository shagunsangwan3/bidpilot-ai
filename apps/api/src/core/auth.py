from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session

from src.utils.security import SECRET_KEY, ALGORITHM
from src.core.dependencies import get_db
from src.models.user import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # Stateless JWTs can't be individually revoked before they expire — this is
    # what makes "log out of other sessions" actually work. Tokens issued
    # before that action carry the old token_version and get rejected here,
    # even though they're not otherwise expired.
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user or user.token_version != payload.get("token_version"):
        raise HTTPException(
            status_code=401,
            detail="Session expired, please log in again",
        )

    return payload