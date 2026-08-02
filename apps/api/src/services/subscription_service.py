from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.subscription import Subscription


def check_proposal_limit(
    db: Session,
    organization_id: int,
):
    subscription = (
        db.query(Subscription)
        .filter(Subscription.organization_id == organization_id)
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


def check_ai_credit_limit(
    db: Session,
    organization_id: int,
):
    """Used by AI Assistant actions (summarize, draft email, suggest pricing,
    improve text) — these consume ai_credit_used but not proposal_used, since
    they aren't proposal generations."""
    subscription = (
        db.query(Subscription)
        .filter(Subscription.organization_id == organization_id)
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if subscription.ai_credit_used >= subscription.ai_credit_limit:
        raise HTTPException(
            status_code=403,
            detail="AI credit limit exceeded. Upgrade your plan.",
        )

    return subscription