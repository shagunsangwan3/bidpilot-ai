from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.subscription import Subscription


def check_proposal_limit(
    db: Session,
    user_id: int,
):
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    if subscription.proposal_used >= subscription.proposal_limit:
        raise HTTPException(
            status_code=403,
            detail="Proposal limit exceeded. Upgrade your plan.",
        )

    return subscription