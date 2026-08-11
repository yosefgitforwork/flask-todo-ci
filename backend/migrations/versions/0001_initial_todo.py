"""initial todo table

Revision ID: 0001_initial_todo
Revises:
Create Date: 2026-07-22 00:00:00.000000

This migration reflects the EXISTING `todo` table shape (id / title / complete)
so Flask-Migrate can be adopted without redesigning the database:

  * Fresh database:            `flask db upgrade` creates the table.
  * Existing database + data:  `flask db stamp head` records this revision as
                               already applied WITHOUT touching your data.

See the README's "Database migrations" section for the full flow.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial_todo"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "todo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("complete", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("todo")
