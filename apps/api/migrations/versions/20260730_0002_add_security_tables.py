"""add security fields and login_sessions table

Revision ID: 20260730_0002
Revises: 20260730_0001
Create Date: 2026-07-30

Same IF NOT EXISTS approach as the previous migration, for the same reason:
safe whether the DB already has these (via create_all() on a fresh deploy,
since the models now define them) or doesn't yet (the real deployed DB this
is written for).
"""
from alembic import op


revision = "20260730_0002"
down_revision = "20260730_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMPTZ"
    )
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version INTEGER NOT NULL DEFAULT 1"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS login_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            ip_address VARCHAR(64),
            user_agent VARCHAR(500),
            browser VARCHAR(100),
            operating_system VARCHAR(100),
            location VARCHAR(150),
            revoked BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT now(),
            last_seen_at TIMESTAMPTZ DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_login_sessions_user_id ON login_sessions (user_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS login_sessions")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS token_version")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS password_changed_at")
