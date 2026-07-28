from sqlalchemy.orm import Session

from src.models.proposal_template import ProposalTemplate


def seed_templates(db: Session):
    if db.query(ProposalTemplate).count() > 0:
        return

    templates = [
        ProposalTemplate(
            name="Web Development",
            category="Web",
            description="Professional website proposal",
            content="""Create a professional website using React, FastAPI and PostgreSQL.

Scope:
- Responsive UI
- Authentication
- Dashboard
- Admin Panel
- Deployment

Timeline:
4 Weeks

Technologies:
React
FastAPI
PostgreSQL
Docker
""",
        ),
        ProposalTemplate(
            name="Mobile App",
            category="Mobile",
            description="Android & iOS application",
            content="""Build a cross-platform mobile application.

Scope:
- Login
- Push Notifications
- Payments
- Admin Dashboard

Timeline:
6 Weeks
""",
        ),
        ProposalTemplate(
            name="AI / Machine Learning",
            category="AI",
            description="AI powered solution",
            content="""Develop an AI solution using Python.

Scope:
- Data Collection
- Model Training
- API Development
- Deployment
""",
        ),
        ProposalTemplate(
            name="Data Analytics",
            category="Data",
            description="Power BI Dashboard",
            content="""Create business dashboards.

Deliverables:
- Power BI Dashboard
- KPI Report
- SQL Queries
- Insights Report
""",
        ),
    ]

    db.add_all(templates)
    db.commit()