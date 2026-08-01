from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.auth import require_min_role
from src.core.dependencies import get_db

from src.models.lead import Lead
from src.models.email import Email
from src.models.user import User
from src.models.subscription import Subscription

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _month_key(d: datetime) -> str:
    return d.strftime("%Y-%m")


@router.get("/overview")
def analytics_overview(
    current_user=Depends(require_min_role("manager")),
    db: Session = Depends(get_db),
):
    organization_id = current_user["organization_id"]

    leads = db.query(Lead).filter(Lead.organization_id == organization_id).all()

    total_leads = len(leads)
    won_leads = [l for l in leads if l.status == "won"]
    lost_leads = [l for l in leads if l.status == "lost"]

    total_revenue = sum(l.budget or 0 for l in won_leads)
    avg_deal_size = total_revenue / len(won_leads) if won_leads else 0

    conversion_rate = (len(won_leads) / total_leads * 100) if total_leads else 0
    decided = len(won_leads) + len(lost_leads)
    win_rate = (len(won_leads) / decided * 100) if decided else 0

    # --- Monthly revenue, last 6 months ---
    now = datetime.utcnow()
    month_buckets = []
    cursor = now.replace(day=1)
    for i in range(6):
        month_buckets.append(cursor.strftime("%Y-%m"))
        # Step back one month (avoids adding a relativedelta dependency for this).
        prev_day = cursor - timedelta(days=1)
        cursor = prev_day.replace(day=1)
    month_buckets.reverse()

    revenue_by_month = defaultdict(float)
    for l in won_leads:
        if l.won_at:
            revenue_by_month[_month_key(l.won_at)] += l.budget or 0

    monthly_revenue = [
        {"month": m, "revenue": round(revenue_by_month.get(m, 0), 2)} for m in month_buckets
    ]

    # --- Lead sources ---
    source_counts = defaultdict(int)
    for l in leads:
        source_counts[l.platform or "Unknown"] += 1
    lead_sources = [{"source": k, "count": v} for k, v in sorted(source_counts.items(), key=lambda x: -x[1])]

    # --- Top customers (by won revenue) ---
    customer_revenue = defaultdict(float)
    for l in won_leads:
        customer_revenue[l.client_name] += l.budget or 0
    top_customers = [
        {"name": k, "revenue": round(v, 2)}
        for k, v in sorted(customer_revenue.items(), key=lambda x: -x[1])[:5]
    ]

    # --- Top sales members (by won revenue, attributed to the lead's creator) ---
    member_stats = defaultdict(lambda: {"won_count": 0, "revenue": 0.0})
    for l in won_leads:
        member_stats[l.user_id]["won_count"] += 1
        member_stats[l.user_id]["revenue"] += l.budget or 0

    user_names = {
        u.id: u.name
        for u in db.query(User).filter(User.organization_id == organization_id).all()
    }
    top_sales_members = [
        {
            "user_id": uid,
            "name": user_names.get(uid, "Unknown"),
            "won_count": stats["won_count"],
            "revenue": round(stats["revenue"], 2),
        }
        for uid, stats in sorted(member_stats.items(), key=lambda x: -x[1]["revenue"])[:5]
    ]

    # --- Average response time (lead created -> first outgoing email) ---
    lead_ids = [l.id for l in leads]
    response_hours = []
    if lead_ids:
        first_replies = (
            db.query(Email)
            .filter(Email.lead_id.in_(lead_ids), Email.direction == "outgoing")
            .order_by(Email.lead_id, Email.created_at.asc())
            .all()
        )
        seen_leads = set()
        lead_created = {l.id: l.created_at for l in leads}
        for email in first_replies:
            if email.lead_id in seen_leads:
                continue
            seen_leads.add(email.lead_id)
            created = lead_created.get(email.lead_id)
            if created and email.created_at:
                delta_hours = (email.created_at - created).total_seconds() / 3600
                if delta_hours >= 0:
                    response_hours.append(delta_hours)

    avg_response_time_hours = (
        round(sum(response_hours) / len(response_hours), 1) if response_hours else None
    )

    # --- Subscription / AI usage ---
    subscription = (
        db.query(Subscription)
        .filter(Subscription.organization_id == organization_id)
        .first()
    )
    subscription_usage = None
    if subscription:
        subscription_usage = {
            "plan": subscription.plan,
            "proposal_used": subscription.proposal_used,
            "proposal_limit": subscription.proposal_limit,
            "ai_credit_used": subscription.ai_credit_used,
            "ai_credit_limit": subscription.ai_credit_limit,
        }

    return {
        "total_revenue": round(total_revenue, 2),
        "avg_deal_size": round(avg_deal_size, 2),
        "conversion_rate": round(conversion_rate, 1),
        "win_rate": round(win_rate, 1),
        "total_leads": total_leads,
        "won_leads": len(won_leads),
        "lost_leads": len(lost_leads),
        "monthly_revenue": monthly_revenue,
        "lead_sources": lead_sources,
        "top_customers": top_customers,
        "top_sales_members": top_sales_members,
        "avg_response_time_hours": avg_response_time_hours,
        "subscription_usage": subscription_usage,
    }
