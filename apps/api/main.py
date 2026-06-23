from fastapi import FastAPI

from src.database import Base, engine
from src.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BidPilot AI")

@app.get("/")
def root():
    return {"message": "BidPilot AI Running"}