from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.auth import get_current_user
from src.schemas.auth import RegisterRequest, LoginRequest
from src.models.user import User
from src.core.dependencies import get_db
from src.models.subscription import Subscription
from src.utils.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if existing_user:
        return {
            "success": False,
            "message": "Email already registered"
        }

    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    subscription = Subscription(
    user_id=user.id,
    plan="Free",
    status="active",
    proposal_limit=3,
    proposal_used=0,
    ai_credit_limit=10,
    ai_credit_used=0,
)

    db.add(subscription)
    db.commit()

    return {
        "success": True,
        "user_id": user.id,
        "email": user.email
    }

@router.post("/login")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if not user:
        return {
            "success": False,
            "message": "Invalid credentials"
        }

    if not verify_password(
        payload.password,
        user.password
    ):
        return {
            "success": False,
            "message": "Invalid credentials"
        }

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email
        }
    )

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == current_user["user_id"])
        .first()
    )

    if not user:
        return {
            "success": False,
            "message": "User not found"
        }

    return {
        "success": True,
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }