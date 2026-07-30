import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.core.auth import get_current_user
from src.schemas.auth import RegisterRequest, LoginRequest, UpdateProfileRequest
from src.models.user import User
from src.core.dependencies import get_db
from src.models.subscription import Subscription
from src.utils.security import (
    hash_password,
    verify_password,
    create_access_token
)

AVATAR_UPLOAD_FOLDER = "uploads/avatars"
COVER_UPLOAD_FOLDER = "uploads/covers"
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB — mirrors the frontend's own check

os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COVER_UPLOAD_FOLDER, exist_ok=True)

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
        # Previously returned HTTP 200 with {success: false}, which the frontend's
        # request() helper treats as a successful response (it only throws on non-2xx).
        # That silently let a duplicate-email registration fall through as if it worked.
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

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

    # Previously this endpoint never issued a token at all, so a *successful*
    # registration still left the frontend calling setToken(undefined) and
    # navigating to the dashboard with no valid session.
    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email
        }
    )

    return {
        "success": True,
        "user_id": user.id,
        "email": user.email,
        "access_token": token,
        "token_type": "bearer",
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

    # Previously both of these returned HTTP 200 with {success: false}. The frontend's
    # request() helper only throws on a non-2xx status, so a wrong password resolved as
    # a "successful" response with no access_token — login.tsx then stored an undefined
    # token and navigated to /dashboard as if the login had worked.
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

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

def _serialize_user(user: User) -> dict:
    return {
        "success": True,
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "username": user.username,
        "mobile_number": user.mobile_number,
        "alt_mobile_number": user.alt_mobile_number,
        "country_code": user.country_code,
        "date_of_birth": user.date_of_birth,
        "gender": user.gender,
        "company": user.company,
        "designation": user.designation,
        "department": user.department,
        "website": user.website,
        "linkedin": user.linkedin,
        "twitter": user.twitter,
        "github": user.github,
        "bio": user.bio,
        "description": user.description,
        "timezone": user.timezone,
        "country": user.country,
        "state": user.state,
        "city": user.city,
        "address": user.address,
        "zip_code": user.zip_code,
        # Relative paths, same pattern as attachments — the frontend fetches
        # these as authenticated blobs rather than a public <img src>, since
        # this endpoint requires the same Bearer auth as everything else.
        "profile_picture_url": (
            "/auth/me/avatar" if user.profile_picture_path else None
        ),
        "cover_image_url": (
            "/auth/me/cover-image" if user.cover_image_path else None
        ),
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

    return _serialize_user(user)


@router.patch("/me")
def update_me(
    payload: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == current_user["user_id"])
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.username and payload.username != user.username:
        existing = (
            db.query(User)
            .filter(User.username == payload.username, User.id != user.id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

    for field, value in payload.model_dump().items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return _serialize_user(user)


def _save_image(file: UploadFile, folder: str) -> str:
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, or WebP images are supported",
        )

    # FastAPI's UploadFile doesn't expose a reliable pre-read size, so this
    # reads once, checks it, then writes — the frontend also enforces this
    # limit before ever uploading, this is the server-side backstop.
    contents = file.file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image must be under 5MB")

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    filename = f"{uuid4()}{ext}"
    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(contents)

    return filepath


@router.post("/me/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_path = user.profile_picture_path
    user.profile_picture_path = _save_image(file, AVATAR_UPLOAD_FOLDER)
    db.commit()

    if old_path and os.path.exists(old_path):
        os.remove(old_path)

    return {"success": True, "profile_picture_url": "/auth/me/avatar"}


@router.delete("/me/avatar")
def delete_avatar(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.profile_picture_path and os.path.exists(user.profile_picture_path):
        os.remove(user.profile_picture_path)

    user.profile_picture_path = None
    db.commit()

    return {"success": True}


@router.get("/me/avatar")
def get_avatar(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user or not user.profile_picture_path or not os.path.exists(user.profile_picture_path):
        raise HTTPException(status_code=404, detail="No profile picture set")

    return FileResponse(user.profile_picture_path)


@router.post("/me/cover-image")
def upload_cover_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_path = user.cover_image_path
    user.cover_image_path = _save_image(file, COVER_UPLOAD_FOLDER)
    db.commit()

    if old_path and os.path.exists(old_path):
        os.remove(old_path)

    return {"success": True, "cover_image_url": "/auth/me/cover-image"}


@router.delete("/me/cover-image")
def delete_cover_image(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.cover_image_path and os.path.exists(user.cover_image_path):
        os.remove(user.cover_image_path)

    user.cover_image_path = None
    db.commit()

    return {"success": True}


@router.get("/me/cover-image")
def get_cover_image(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user or not user.cover_image_path or not os.path.exists(user.cover_image_path):
        raise HTTPException(status_code=404, detail="No cover image set")

    return FileResponse(user.cover_image_path)