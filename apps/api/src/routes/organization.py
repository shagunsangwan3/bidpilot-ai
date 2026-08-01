import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.core.auth import get_current_user, require_min_role
from src.core.dependencies import get_db
from src.models.organization import Organization, OrganizationInvite, VALID_ROLES, ROLE_RANK
from src.models.user import User
from src.schemas.organization import UpdateOrganizationRequest, InviteMemberRequest, ChangeRoleRequest
from src.services.email_service import send_email

router = APIRouter(prefix="/organizations", tags=["Organizations"])

LOGO_UPLOAD_FOLDER = "uploads/logos"
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
os.makedirs(LOGO_UPLOAD_FOLDER, exist_ok=True)


def _serialize_org(org: Organization, role: str) -> dict:
    return {
        "id": org.id,
        "name": org.name,
        "address": org.address,
        "gst_number": org.gst_number,
        "website": org.website,
        "industry": org.industry,
        "employee_count": org.employee_count,
        "logo_url": "/organizations/me/logo" if org.logo_path else None,
        "my_role": role,
    }


@router.get("/me")
def get_organization(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = db.query(Organization).filter(Organization.id == current_user["organization_id"]).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return _serialize_org(org, current_user["role"])


@router.patch("/me")
def update_organization(
    payload: UpdateOrganizationRequest,
    current_user=Depends(require_min_role("admin")),
    db: Session = Depends(get_db),
):
    org = db.query(Organization).filter(Organization.id == current_user["organization_id"]).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    for field, value in payload.model_dump().items():
        setattr(org, field, value)

    db.commit()
    db.refresh(org)

    return _serialize_org(org, current_user["role"])


@router.post("/me/logo")
def upload_logo(
    file: UploadFile = File(...),
    current_user=Depends(require_min_role("admin")),
    db: Session = Depends(get_db),
):
    org = db.query(Organization).filter(Organization.id == current_user["organization_id"]).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WebP images are supported")

    contents = file.file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image must be under 5MB")

    old_path = org.logo_path
    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    filepath = os.path.join(LOGO_UPLOAD_FOLDER, f"{uuid4()}{ext}")
    with open(filepath, "wb") as buffer:
        buffer.write(contents)

    org.logo_path = filepath
    db.commit()

    if old_path and os.path.exists(old_path):
        os.remove(old_path)

    return {"success": True, "logo_url": "/organizations/me/logo"}


@router.get("/me/logo")
def get_logo(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = db.query(Organization).filter(Organization.id == current_user["organization_id"]).first()
    if not org or not org.logo_path or not os.path.exists(org.logo_path):
        raise HTTPException(status_code=404, detail="No logo set")
    return FileResponse(org.logo_path)


@router.delete("/me/logo")
def delete_logo(
    current_user=Depends(require_min_role("admin")),
    db: Session = Depends(get_db),
):
    org = db.query(Organization).filter(Organization.id == current_user["organization_id"]).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if org.logo_path and os.path.exists(org.logo_path):
        os.remove(org.logo_path)
    org.logo_path = None
    db.commit()

    return {"success": True}


@router.get("/members")
def list_members(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    members = (
        db.query(User)
        .filter(User.organization_id == current_user["organization_id"])
        .all()
    )

    invites = (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.organization_id == current_user["organization_id"])
        .all()
    )

    return {
        "members": [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                "role": m.role,
                "profile_picture_url": "/auth/me/avatar" if m.profile_picture_path else None,
            }
            for m in members
        ],
        "pending_invites": [
            {"id": i.id, "email": i.email, "role": i.role, "created_at": i.created_at}
            for i in invites
        ],
    }


@router.post("/invite")
async def invite_member(
    payload: InviteMemberRequest,
    current_user=Depends(require_min_role("manager")),
    db: Session = Depends(get_db),
):
    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Role must be one of {VALID_ROLES}")

    # A manager can't invite someone at admin/owner level above their own rank.
    if ROLE_RANK[payload.role] >= ROLE_RANK[current_user["role"]]:
        raise HTTPException(status_code=403, detail="You can't invite someone at or above your own role")

    existing_member = (
        db.query(User)
        .filter(User.email == payload.email, User.organization_id == current_user["organization_id"])
        .first()
    )
    if existing_member:
        raise HTTPException(status_code=400, detail="This person is already a member")

    existing_invite = (
        db.query(OrganizationInvite)
        .filter(
            OrganizationInvite.email == payload.email,
            OrganizationInvite.organization_id == current_user["organization_id"],
        )
        .first()
    )
    if existing_invite:
        raise HTTPException(status_code=400, detail="An invite is already pending for this email")

    invite = OrganizationInvite(
        organization_id=current_user["organization_id"],
        email=payload.email,
        role=payload.role,
        invited_by=current_user["user_id"],
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    try:
        await send_email(
            to=payload.email,
            subject="You've been invited to join a team on BidPilot AI",
            body=(
                f"You've been invited to join a team as {payload.role}. "
                "Register or log in with this email address to join automatically."
            ),
        )
    except Exception:
        # Don't fail the invite itself if outbound mail isn't configured/working —
        # the invite row still exists and will auto-join them at registration.
        pass

    return {"id": invite.id, "email": invite.email, "role": invite.role}


@router.delete("/invites/{invite_id}")
def cancel_invite(
    invite_id: int,
    current_user=Depends(require_min_role("manager")),
    db: Session = Depends(get_db),
):
    invite = (
        db.query(OrganizationInvite)
        .filter(
            OrganizationInvite.id == invite_id,
            OrganizationInvite.organization_id == current_user["organization_id"],
        )
        .first()
    )
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    db.delete(invite)
    db.commit()

    return {"success": True}


@router.post("/invites/{invite_id}/accept")
def accept_invite(
    invite_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """For an already-registered user accepting an invite to a *different*
    org than the one they're currently in (the common case — a brand new
    user with no account yet — is handled automatically at registration)."""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()

    invite = db.query(OrganizationInvite).filter(OrganizationInvite.id == invite_id).first()
    if not invite or invite.email != user.email:
        raise HTTPException(status_code=404, detail="Invite not found")

    user.organization_id = invite.organization_id
    user.role = invite.role
    db.delete(invite)
    db.commit()

    return {"success": True, "organization_id": user.organization_id, "role": user.role}


@router.patch("/members/{user_id}/role")
def change_member_role(
    user_id: int,
    payload: ChangeRoleRequest,
    current_user=Depends(require_min_role("admin")),
    db: Session = Depends(get_db),
):
    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Role must be one of {VALID_ROLES}")

    member = (
        db.query(User)
        .filter(User.id == user_id, User.organization_id == current_user["organization_id"])
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == "owner":
        raise HTTPException(status_code=400, detail="The organization owner's role can't be changed")

    if ROLE_RANK[payload.role] >= ROLE_RANK[current_user["role"]] and current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="You can't grant a role at or above your own")

    member.role = payload.role
    db.commit()

    return {"success": True, "user_id": member.id, "role": member.role}


@router.delete("/members/{user_id}")
def remove_member(
    user_id: int,
    current_user=Depends(require_min_role("admin")),
    db: Session = Depends(get_db),
):
    member = (
        db.query(User)
        .filter(User.id == user_id, User.organization_id == current_user["organization_id"])
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == "owner":
        raise HTTPException(status_code=400, detail="The organization owner can't be removed")

    if member.id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="You can't remove yourself — leave that to another admin")

    # Give the removed member their own personal organization rather than
    # leaving them with a dangling/null organization_id, which every other
    # route assumes is always set.
    new_org = Organization(name=f"{member.name}'s Organization", created_by=member.id)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    member.organization_id = new_org.id
    member.role = "owner"
    db.commit()

    return {"success": True}
