"""create auditable vacation balance ledger

Revision ID: 20260726_0009
Revises: 20260723_0008
Create Date: 2026-07-26
"""

from datetime import date, datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260726_0009"
down_revision: Union[str, None] = "20260723_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "proxima_concessao_ferias" not in columns:
        op.add_column("users", sa.Column("proxima_concessao_ferias", sa.Date(), nullable=True))

    if "saldo_ferias_movimentos" not in sa.inspect(bind).get_table_names():
        op.create_table(
            "saldo_ferias_movimentos",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tipo", sa.String(), nullable=False),
            sa.Column("quantidade_dias", sa.Integer(), nullable=False),
            sa.Column("data_referencia", sa.Date(), nullable=False),
            sa.Column("motivo", sa.String(), nullable=True),
            sa.Column("criado_por_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("chave_idempotencia", sa.String(), nullable=False),
            sa.Column("criado_em", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("chave_idempotencia", name="uq_saldo_ferias_movimento_chave"),
        )
        op.create_index("ix_saldo_ferias_movimentos_user_id", "saldo_ferias_movimentos", ["user_id"])

    users = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("dias_totais", sa.Integer()),
        sa.column("saldo_manual_dias", sa.Integer()),
    )
    movimentos = sa.table(
        "saldo_ferias_movimentos",
        sa.column("user_id", sa.Integer()),
        sa.column("tipo", sa.String()),
        sa.column("quantidade_dias", sa.Integer()),
        sa.column("data_referencia", sa.Date()),
        sa.column("motivo", sa.String()),
        sa.column("criado_por_id", sa.Integer()),
        sa.column("chave_idempotencia", sa.String()),
        sa.column("criado_em", sa.DateTime()),
    )
    agora = datetime.utcnow()
    existentes = {
        row[0] for row in bind.execute(
            sa.text("SELECT user_id FROM saldo_ferias_movimentos WHERE tipo = 'saldo_inicial'")
        )
    }
    registros = []
    for row in bind.execute(sa.select(users.c.id, users.c.dias_totais, users.c.saldo_manual_dias)):
        if row.id in existentes:
            continue
        saldo = row.saldo_manual_dias if row.saldo_manual_dias is not None else (row.dias_totais or 30)
        registros.append({
            "user_id": row.id,
            "tipo": "saldo_inicial",
            "quantidade_dias": saldo,
            "data_referencia": date.today(),
            "motivo": "Saldo inicial migrado na implantacao do controle por movimentacoes.",
            "criado_por_id": None,
            "chave_idempotencia": f"saldo-inicial:{row.id}",
            "criado_em": agora,
        })
    if registros:
        op.bulk_insert(movimentos, registros)


def downgrade() -> None:
    op.drop_table("saldo_ferias_movimentos")
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "proxima_concessao_ferias" in columns:
        op.drop_column("users", "proxima_concessao_ferias")
