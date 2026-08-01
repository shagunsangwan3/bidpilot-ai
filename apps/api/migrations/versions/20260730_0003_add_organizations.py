"""add organizations, team membership, and org-scope existing data

Revision ID: 20260730_0003
Revises: 20260730_0002
Create Date: 2026-07-30

Same IF NOT EXISTS approach as prior migrations. This one also backfills
data: every existing user gets their own personal Organization (as "owner"),
and every one of their existing leads/proposals/subscriptions/payments gets
organization_id set to it. Existing proposal_templates are deliberately left
with organization_id = NULL rather than guessed at — they had no ownership
field at all before this, so there's no reliable way to know which user
"owns" a pre-existing template. NULL is treated by the application as a
legacy/global template visible to everyone, which preserves current (if
questionable) behavior rather than silently hiding templates from the people
who made them.
"""
from alembic import op


revision = "20260730_0003"
down_revision = "20260730_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS organizations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            logo_path VARCHAR(500),
            address VARCHAR(255),
            gst_number VARCHAR(50),
            website VARCHAR(255),
            industry VARCHAR(150),
            employee_count VARCHAR(30),
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMPTZ DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS organization_invites (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            email VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'sales',
            invited_by INTEGER REFERENCES users(id),
            created_at TIMESTAMPTZ DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_organization_invites_email ON organization_invites (email)"
    )

    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'owner'")

    op.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_leads_organization_id ON leads (organization_id)")

    op.execute("ALTER TABLE proposals ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)")
    op.execute("ALTER TABLE proposals ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_proposals_organization_id ON proposals (organization_id)")

    op.execute("ALTER TABLE proposal_templates ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)")
    op.execute("ALTER TABLE proposal_templates ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_proposal_templates_organization_id ON proposal_templates (organization_id)")

    op.execute("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_subscriptions_organization_id ON subscriptions (organization_id)")

    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payments_organization_id ON payments (organization_id)")

    # --- Data backfill: one personal organization per existing user ---
    # Only touches users who don't already have one (safe to re-run).
    op.execute(
        """
        INSERT INTO organizations (name, created_by, created_at)
        SELECT u.name || '''s Organization', u.id, now()
        FROM users u
        WHERE u.organization_id IS NULL
        """
    )

    # Match each newly-created org back to the user that created it (by
    # created_by, which is unique per row inserted above) and assign it.
    op.execute(
        """
        UPDATE users u
        SET organization_id = o.id, role = 'owner'
        FROM organizations o
        WHERE o.created_by = u.id AND u.organization_id IS NULL
        """
    )

    op.execute(
        """
        UPDATE leads l
        SET organization_id = u.organization_id
        FROM users u
        WHERE l.user_id = u.id AND l.organization_id IS NULL
        """
    )

    op.execute(
        """
        UPDATE proposals p
        SET organization_id = l.organization_id, created_by = l.user_id
        FROM leads l
        WHERE p.lead_id = l.id AND p.organization_id IS NULL
        """
    )

    op.execute(
        """
        UPDATE subscriptions s
        SET organization_id = u.organization_id
        FROM users u
        WHERE s.user_id = u.id AND s.organization_id IS NULL
        """
    )

    op.execute(
        """
        UPDATE payments p
        SET organization_id = u.organization_id
        FROM users u
        WHERE p.user_id = u.id AND p.organization_id IS NULL
        """
    )


def downgrade() -> None:
    for table in ("payments", "subscriptions", "proposal_templates", "proposals", "leads"):
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS organization_id")
    op.execute("ALTER TABLE proposals DROP COLUMN IF EXISTS created_by")
    op.execute("ALTER TABLE proposal_templates DROP COLUMN IF EXISTS created_by")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS role")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS organization_id")
    op.execute("DROP TABLE IF EXISTS organization_invites")
    op.execute("DROP TABLE IF EXISTS organizations")
