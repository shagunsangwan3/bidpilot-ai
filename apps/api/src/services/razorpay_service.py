import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET"),
    )
)


def create_subscription(plan_id: str, total_count: int = 12):
    """
    Creates a Razorpay subscription.

    total_count:
    12 = 12 billing cycles (e.g. monthly for 1 year)
    1 = one cycle
    """
    return client.subscription.create(
        {
            "plan_id": plan_id,
            "total_count": total_count,
            "customer_notify": 1,
        }
    )