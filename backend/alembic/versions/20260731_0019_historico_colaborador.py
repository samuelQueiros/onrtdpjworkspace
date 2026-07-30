"""cria historico funcional (cargo/departamento/beneficios) dos colaboradores

Revision ID: 20260731_0019
Revises: 20260730_0018
"""

import sqlalchemy as sa
from alembic import op


revision = "20260731_0019"
down_revision = "20260730_0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "historico_colaborador",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("campo", sa.String(length=30), nullable=False),
        sa.Column("valor_anterior_criptografado", sa.Text(), nullable=True),
        sa.Column("valor_novo_criptografado", sa.Text(), nullable=False),
        sa.Column("tipo_alteracao", sa.String(length=20), nullable=False, server_default="real"),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column("data_vigencia", sa.Date(), nullable=False),
        sa.Column("criado_por_id", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "campo IN ('cargo','departamento','valor_beneficios')",
            name="ck_historico_colaborador_campo",
        ),
        sa.CheckConstraint(
            "tipo_alteracao IN ('real','correcao')",
            name="ck_historico_colaborador_tipo_alteracao",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criado_por_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_historico_colaborador_user_campo_data",
        "historico_colaborador",
        ["user_id", "campo", "data_vigencia"],
    )


def downgrade() -> None:
    op.drop_index("ix_historico_colaborador_user_campo_data", table_name="historico_colaborador")
    op.drop_table("historico_colaborador")
