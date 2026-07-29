"""adiciona observacao aos documentos

Revision ID: 20260729_0013
Revises: 20260728_0012
"""

import sqlalchemy as sa
from alembic import op


revision = "20260729_0013"
down_revision = "20260728_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documentos",
        sa.Column("observacao", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documentos", "observacao")
