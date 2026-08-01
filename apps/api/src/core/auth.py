from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session

from src.utils.security import SECRET_KEY, ALGORITHM
from src.core.dependencies import get_db
from src.models.user import User
from src.models.organization import ROLE_RANK

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

    # organization_id/role come from the DB on every request rather than the
    # JWT's own claims — a role change (or being removed from an org) takes
    # effect on the user's very next request instead of only after their
    # token expires or they're forced to re-login.
    payload["organization_id"] = user.organization_id
    payload["role"] = user.role

    return payload


def require_role(*allowed_roles: str):
    """Dependency factory: raises 403 unless the caller's role is one of
    allowed_roles. Usage: Depends(require_role("admin", "owner"))."""

    def _check(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to do this",
            )
        return current_user

    return _check


def require_min_role(minimum: str):
    """Like require_role, but by rank — require_min_role('admin') allows
    admin and owner (anything ranked at or above 'admin')."""

    def _check(current_user: dict = Depends(get_current_user)) -> dict:
        role = current_user.get("role")
        if ROLE_RANK.get(role, -1) < ROLE_RANK.get(minimum, 999):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to do this",
            )
        return current_user

    return _check