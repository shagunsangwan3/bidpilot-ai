from sqlalchemy import ForeignKey

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey
)

from src.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255))
    platform = Column(String(100))
    budget = Column(String(100))
    description = Column(Text)

    status = Column(
        String(50),
        default="new"
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )