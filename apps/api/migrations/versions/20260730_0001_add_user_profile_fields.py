"""add user profile fields

Revision ID: 20260730_0001
Revises:
Create Date: 2026-07-30

This is the first Alembic revision for this project. The app previously
relied solely on Base.metadata.create_all() at startup, which creates
missing tables but never alters existing ones — so this migration is
written to be safe to run against BOTH:
  - an existing database that already has a `users` table without these
    columns (the real-world case this migration exists for), and
  - a brand-new database where create_all() already created `users` with
    these columns present (since the model now defines them), where this
    migration should simply be a no-op.

`ADD COLUMN IF NOT EXISTS` (native to Postgres) makes it safe either way,
which plain Alembic op.add_column() does not support — hence raw SQL via
op.execute() instead of the usual op.add_column() calls.

To apply: run `alembic upgrade head` once after deploying this change.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "20260730_0001"
down_revision = None
branch_labels = None
depends_on = None


NEW_COLUMNS = [
    ("username", "VARCHAR(50)"),
    ("mobile_number", "VARCHAR(20)"),
    ("alt_mobile_number", "VARCHAR(20)"),
    ("country_code", "VARCHAR(8)"),
    ("date_of_birth", "DATE"),
    ("gender", "VARCHAR(30)"),
    ("company", "VARCHAR(150)"),
    ("designation", "VARCHAR(150)"),
    ("department", "VARCHAR(150)"),
    ("website", "VARCHAR(255)"),
    ("linkedin", "VARCHAR(255)"),
    ("twitter", "VARCHAR(255)"),
    ("github", "VARCHAR(255)"),
    ("bio", "VARCHAR(280)"),
    ("description", "TEXT"),
    ("timezone", "VARCHAR(100)"),
    ("country", "VARCHAR(100)"),
    ("state", "VARCHAR(100)"),
    ("city", "VARCHAR(100)"),
    ("address", "VARCHAR(255)"),
    ("zip_code", "VARCHAR(20)"),
    ("profile_picture_path", "VARCHAR(500)"),
    ("cover_image_path", "VARCHAR(500)"),
]


def upgrade() -> None:
    for name, col_type in NEW_COLUMNS:
        op.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {name} {col_type}")

    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at "
        "TIMESTAMPTZ DEFAULT now()"
    )

    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username "
        "ON users (username) WHERE username IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_username")

    for name, _ in NEW_COLUMNS:
        op.execute(f"ALTER TABLE users DROP COLUMN IF EXISTS {name}")

    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS updated_at")
