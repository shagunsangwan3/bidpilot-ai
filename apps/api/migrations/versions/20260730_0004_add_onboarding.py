"""add has_completed_onboarding to users

Revision ID: 20260730_0004
Revises: 20260730_0003
Create Date: 2026-07-30
"""
from alembic import op


revision = "20260730_0004"
down_revision = "20260730_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS has_completed_onboarding "
        "BOOLEAN NOT NULL DEFAULT false"
    )
    # Existing users shouldn't be shown an onboarding wizard the next time
    # they log in — only genuinely new signups should see it.
    op.execute(
        "UPDATE users SET has_completed_onboarding = true WHERE has_completed_onboarding = false"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS has_completed_onboarding")
