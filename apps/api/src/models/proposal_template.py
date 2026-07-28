from sqlalchemy import Column, Integer, String, Text

from src.database import Base


class ProposalTemplate(Base):
    __tablename__ = "proposal_templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    category = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    content = Column(Text, nullable=False)