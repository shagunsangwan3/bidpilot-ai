from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.proposal_template import ProposalTemplate
from src.schemas.proposal_template import ProposalTemplateCreate


router = APIRouter(
    prefix="/templates",
    tags=["Proposal Templates"],
)


@router.get("/")
def get_templates(db: Session = Depends(get_db)):
    templates = db.query(ProposalTemplate).all()

    return templates



@router.post("/")
def create_template(
    template: ProposalTemplateCreate,
    db: Session = Depends(get_db),
):
    new_template = ProposalTemplate(
        name=template.name,
        category=template.category,
        description=template.description,
        content=template.content,
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


@router.put("/{template_id}")
def update_template(
    template_id: int,
    template: ProposalTemplateCreate,
    db: Session = Depends(get_db),
):
    db_template = (
        db.query(ProposalTemplate)
        .filter(ProposalTemplate.id == template_id)
        .first()
    )

    if not db_template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    db_template.name = template.name
    db_template.category = template.category
    db_template.description = template.description
    db_template.content = template.content

    db.commit()
    db.refresh(db_template)

    return db_template

@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    db_template = (
        db.query(ProposalTemplate)
        .filter(ProposalTemplate.id == template_id)
        .first()
    )

    if not db_template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    db.delete(db_template)
    db.commit()

    return {
        "message": "Template deleted successfully"
    }