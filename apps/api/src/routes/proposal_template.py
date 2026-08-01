from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.proposal_template import ProposalTemplate
from src.schemas.proposal_template import ProposalTemplateCreate
from src.core.auth import get_current_user


router = APIRouter(
    prefix="/templates",
    tags=["Proposal Templates"],
)

# CRITICAL: every route in this file previously had no auth dependency at
# all — anyone, unauthenticated, could list/create/edit/delete every
# proposal template in the system. Every route now requires login and scopes
# to the caller's organization. Templates with organization_id = NULL are
# pre-existing rows from before this table had any ownership field — treated
# as legacy "system templates" visible to everyone rather than hidden.


@router.get("/")
def get_templates(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ProposalTemplate)
        .filter(
            (ProposalTemplate.organization_id == current_user["organization_id"])
            | (ProposalTemplate.organization_id.is_(None))
        )
        .all()
    )


@router.post("/")
def create_template(
    template: ProposalTemplateCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_template = ProposalTemplate(
        name=template.name,
        category=template.category,
        description=template.description,
        content=template.content,
        organization_id=current_user["organization_id"],
        created_by=current_user["user_id"],
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


def _get_editable_template(template_id: int, current_user: dict, db: Session) -> ProposalTemplate:
    db_template = (
        db.query(ProposalTemplate)
        .filter(ProposalTemplate.id == template_id)
        .first()
    )

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    # A legacy global template (organization_id IS NULL) can be viewed by
    # everyone but only edited/deleted by someone in the org that (maybe)
    # created it, or left editable by anyone if it truly has no owner —
    # here we allow any authenticated org member to edit a NULL-owner
    # template, since restricting it further would just orphan it with no
    # one able to maintain it.
    if (
        db_template.organization_id is not None
        and db_template.organization_id != current_user["organization_id"]
    ):
        raise HTTPException(status_code=404, detail="Template not found")

    return db_template


@router.put("/{template_id}")
def update_template(
    template_id: int,
    template: ProposalTemplateCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_template = _get_editable_template(template_id, current_user, db)

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
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_template = _get_editable_template(template_id, current_user, db)

    db.delete(db_template)
    db.commit()

    return {
        "message": "Template deleted successfully"
    }
