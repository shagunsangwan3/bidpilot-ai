import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
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


def _serialize(attachment: Attachment) -> dict:
    return {
        "id": attachment.id,
        "lead_id": attachment.lead_id,
        "filename": attachment.filename,
        "created_at": attachment.created_at,
        # Relative path — the frontend resolves this against its own configured API
        # base URL (backend doesn't know its own public origin, there's no BASE_URL
        # env var configured anywhere in this codebase).
        "download_url": f"/attachments/download/{attachment.id}",
    }


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
            Lead.organization_id == current_user["organization_id"],
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

    return _serialize(attachment)

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
            Lead.organization_id == current_user["organization_id"],
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    attachments = (
        db.query(Attachment)
        .filter(Attachment.lead_id == lead.id)
        .all()
    )

    return [_serialize(a) for a in attachments]


@router.get("/download/{attachment_id}")
def download_attachment(
    attachment_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attachment = (
        db.query(Attachment)
        .join(Lead, Lead.id == Attachment.lead_id)
        .filter(
            Attachment.id == attachment_id,
            Lead.organization_id == current_user["organization_id"],
        )
        .first()
    )

    if not attachment or not os.path.exists(attachment.filepath):
        raise HTTPException(status_code=404, detail="Attachment not found")

    return FileResponse(
        attachment.filepath,
        filename=attachment.filename,
    )