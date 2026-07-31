"""corrige logs.criado_em para timestamp com timezone (valores existentes sao UTC)

Revision ID: 20260731_0020
Revises: 20260731_0019
"""

from alembic import op


revision = "20260731_0020"
down_revision = "20260731_0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE logs ALTER COLUMN criado_em TYPE timestamptz USING criado_em AT TIME ZONE 'UTC'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE logs ALTER COLUMN criado_em TYPE timestamp USING criado_em AT TIME ZONE 'UTC'"
    )
