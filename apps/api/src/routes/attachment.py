import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.core.auth import get_current_user
from src.core.dependencies import get_db

from src.models.attachment import Attachment
from src.models.lead import Lead

router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload/{lead_id}")
def upload_attachment(
    lead_id: int,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.user_id == current_user["user_id"],
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    filename = f"{uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    attachment = Attachment(
        lead_id=lead.id,
        filename=file.filename,
        filepath=filepath,
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment

@router.get("/{lead_id}")
def get_attachments(
    lead_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.user_id == current_user["user_id"],
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    return (
        db.query(Attachment)
        .filter(Attachment.lead_id == lead.id)
        .all()
    )