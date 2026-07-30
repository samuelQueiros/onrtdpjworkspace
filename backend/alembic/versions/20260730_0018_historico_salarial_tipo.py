"""adiciona tipo (reajuste/correcao) ao historico salarial

Revision ID: 20260730_0018
Revises: 20260730_0017
"""

import sqlalchemy as sa
from alembic import op


revision = "20260730_0018"
down_revision = "20260730_0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "historico_salarial",
        sa.Column("tipo", sa.String(length=20), nullable=False, server_default="reajuste"),
    )
    op.create_check_constraint(
        "ck_historico_salarial_tipo",
        "historico_salarial",
        "tipo IN ('reajuste','correcao')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_historico_salarial_tipo", "historico_salarial", type_="check")
    op.drop_column("historico_salarial", "tipo")
