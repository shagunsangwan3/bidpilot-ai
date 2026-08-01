from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from src.core.auth import get_current_user, require_min_role
from src.core.dependencies import get_db

from src.models.subscription import Subscription
from src.services.razorpay_service import create_subscription

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


@router.post("/create")
def create_user_subscription(
    current_user=Depends(require_min_role("admin")),
    db: Session = Depends(get_db),
):
    plan_id = os.getenv("RAZORPAY_PLAN_ID")

    if not plan_id:
        raise HTTPException(
            status_code=500,
            detail="RAZORPAY_PLAN_ID is not configured.",
        )

    razorpay_subscription = create_subscription(plan_id)

    # One subscription per organization — billing is a team-level concern,
    # not per individual member.
    subscription = (
        db.query(Subscription)
        .filter(Subscription.organization_id == current_user["organization_id"])
        .first()
    )

    if not subscription:
        subscription = Subscription(
            user_id=current_user["user_id"],
            organization_id=current_user["organization_id"],
        )
        db.add(subscription)

    subscription.razorpay_subscription_id = razorpay_subscription["id"]
    subscription.plan = "Pro"
    subscription.status = razorpay_subscription["status"]

    db.commit()
    db.refresh(subscription)

    return {
        "subscription_id": razorpay_subscription["id"],
        "status": razorpay_subscription["status"],
        "plan": "Pro",
    }


@router.post("/cancel")
def cancel_user_subscription(
    current_user=Depends(require_min_role("admin")),
    db: Session = Depends(get_db),
):
    subscription = (
        db.query(Subscription)
        .filter(Subscription.organization_id == current_user["organization_id"])
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")

    if subscription.plan == "Free":
        raise HTTPException(status_code=400, detail="You're already on the Free plan")

    subscription.plan = "Free"
    subscription.status = "cancelled"

    db.commit()

    return {"success": True}
