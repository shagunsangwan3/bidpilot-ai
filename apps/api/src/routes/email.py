from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db

from src.schemas.email import SendEmailRequest
from src.services.email_service import send_email

from src.models.email import Email

from src.utils.activity_logger import log_activity

router = APIRouter(
    prefix="/email",
    tags=["Email"],
)


@router.post("/send")
async def send_proposal_email(
    payload: SendEmailRequest,
    db: Session = Depends(get_db),
):

    await send_email(
        payload.to,
        payload.subject,
        payload.body,
    )

    email = Email(
        lead_id=payload.lead_id,
        sender="me",
        receiver=payload.to,
        subject=payload.subject,
        body=payload.body,
        direction="outgoing",
        status="sent",
    )

    db.add(email)
    db.commit()

    log_activity(
    db=db,
    lead_id=payload.lead_id,
    action="Email Sent",
    description=f"Email sent to {payload.to}",
    )

    return {
        "success": True,
        "message": "Email sent successfully",
    }