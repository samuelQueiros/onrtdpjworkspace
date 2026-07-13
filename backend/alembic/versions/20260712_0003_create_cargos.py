"""create cargos catalog

Revision ID: 20260712_0003
Revises: 20260712_0002
Create Date: 2026-07-12
"""

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0003"
down_revision: Union[str, None] = "20260712_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CARGOS_INICIAIS = (
    "Gerente Executiva",
    "Gerente Administrativo",
    "Auxiliar Administrativo",
    "Jornalista",
    "Analista de BI",
    "Desenvolvedor",
    "Coordenador de Suporte",
)


def upgrade() -> None:
    bind = op.get_bind()
    if "cargos" not in sa.inspect(bind).get_table_names():
        op.create_table(
            "cargos",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("nome", sa.String(), nullable=False, unique=True),
            sa.Column("criado_em", sa.DateTime(), nullable=True),
        )

    cargos = sa.table(
        "cargos",
        sa.column("nome", sa.String()),
        sa.column("criado_em", sa.DateTime()),
    )
    existentes = {row[0] for row in bind.execute(sa.text("SELECT nome FROM cargos"))}
    agora = datetime.utcnow()
    op.bulk_insert(cargos, [{"nome": nome, "criado_em": agora} for nome in CARGOS_INICIAIS if nome not in existentes])


def downgrade() -> None:
    op.drop_table("cargos")
