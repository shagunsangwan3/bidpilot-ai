from sqlalchemy import *

from src.database import Base


class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
    )

    ai_proposals = Column(Integer, default=0)

    leads = Column(Integer, default=0)

    storage = Column(Float, default=0)