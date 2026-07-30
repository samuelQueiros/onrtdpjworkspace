"""cria historico salarial dos colaboradores

Revision ID: 20260730_0017
Revises: 20260729_0016
"""

import sqlalchemy as sa
from alembic import op


revision = "20260730_0017"
down_revision = "20260729_0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "historico_salarial",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("salario_criptografado", sa.Text(), nullable=False),
        sa.Column("data_vigencia", sa.Date(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column("criado_por_id", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criado_por_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_historico_salarial_user_data",
        "historico_salarial",
        ["user_id", "data_vigencia"],
    )


def downgrade() -> None:
    op.drop_index("ix_historico_salarial_user_data", table_name="historico_salarial")
    op.drop_table("historico_salarial")
