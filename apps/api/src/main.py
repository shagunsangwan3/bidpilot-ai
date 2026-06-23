from fastapi import FastAPI

from src.database import Base, engine
from src.models.user import User
from src.models.lead import Lead

from src.routes.auth import router as auth_router
from src.routes.lead import router as lead_router
from src.routes.proposal import router as proposal_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BidPilot AI",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(lead_router)

@app.get("/")
def root():
    return {
        "message": "BidPilot AI Running"
    }

app.include_router(proposal_router)