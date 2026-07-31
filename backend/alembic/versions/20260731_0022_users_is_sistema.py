"""adiciona users.is_sistema para ocultar contas administrativas de sistema

Revision ID: 20260731_0022
Revises: 20260731_0021
"""

import sqlalchemy as sa
from alembic import op


revision = "20260731_0022"
down_revision = "20260731_0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_sistema",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_sistema")
