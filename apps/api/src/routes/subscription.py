from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from src.core.auth import get_current_user
from src.core.dependencies import get_db

from src.models.subscription import Subscription
from src.services.razorpay_service import create_subscription

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


@router.post("/create")
def create_user_subscription(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan_id = os.getenv("RAZORPAY_PLAN_ID")

    if not plan_id:
        raise HTTPException(
            status_code=500,
            detail="RAZORPAY_PLAN_ID is not configured.",
        )

    razorpay_subscription = create_subscription(plan_id)

    # Previously this always inserted a brand new Subscription row, leaving old rows
    # (e.g. the Free one created at registration) in the table. billing_overview()
    # queries .first() (the oldest row), so an upgraded user would still see "Free"
    # in their billing overview forever. Update the existing row instead so there's
    # one subscription per user, consistent with how billing_overview/cancel read it.
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user["user_id"])
        .first()
    )

    if not subscription:
        subscription = Subscription(user_id=current_user["user_id"])
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
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user["user_id"])
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