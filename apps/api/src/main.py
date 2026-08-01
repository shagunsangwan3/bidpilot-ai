from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import Base, engine

from src.models.user import User
from src.models.lead import Lead
from src.models.proposal import Proposal
from src.models.activity import Activity
from src.models.attachment import Attachment

from src.routes.auth import router as auth_router
from src.routes.lead import router as lead_router
from src.routes.dashboard import router as dashboard_router
from src.routes.proposal import router as proposal_router
from src.routes.activity import router as activity_router
from src.routes.attachment import router as attachment_router
from src.routes.email import router as email_router
from src.routes.inbox import router as inbox_router
from src.routes.billing import router as billing_router
from src.models.notification import Notification
from src.routes.notification import router as notification_router
from src.models.subscription import Subscription
from src.routes.subscription import router as subscription_router
from src.routes.proposal_template import router as proposal_template_router
from src.routes.organization import router as organization_router
from src.routes.organization import router as organization_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BidPilot AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(lead_router)
app.include_router(dashboard_router)
app.include_router(proposal_router)
app.include_router(activity_router)
app.include_router(attachment_router)
app.include_router(email_router)
app.include_router(inbox_router)
app.include_router(billing_router)
app.include_router(notification_router)
app.include_router(subscription_router)
app.include_router(proposal_template_router)
app.include_router(organization_router)

@app.get("/")
def root():
    return {
        "message": "BidPilot AI Running"
    }


