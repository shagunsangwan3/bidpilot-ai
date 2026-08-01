from sqlalchemy import Column, Integer, String, Text, ForeignKey

from src.database import Base


class ProposalTemplate(Base):
    __tablename__ = "proposal_templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    category = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    content = Column(Text, nullable=False)

    # This table previously had NO ownership field at all — every template
    # was visible to and editable by every user in the entire system. Existing
    # rows are backfilled to NULL by the migration (treated as legacy/global
    # "system templates" visible to everyone) rather than guessed at; anything
    # created from here on is scoped to its creating organization.
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
