from fastapi import FastAPI

from src.database import Base, engine
from src.models.user import User

Base.metadata.create_all(bind=engine)

Base.metadata.create_all(bind=engine)

from src.routes.template_seed import seed_templates
from src.database import SessionLocal

db = SessionLocal()
seed_templates(db)
db.close()

app = FastAPI(title="BidPilot AI")

@app.get("/")
def root():
    return {"message": "BidPilot AI Running"}