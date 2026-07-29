"""adiciona departamentos iniciais

Revision ID: 20260729_0014
Revises: 20260729_0013
"""

from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op


revision = "20260729_0014"
down_revision = "20260729_0013"
branch_labels = None
depends_on = None

DEPARTAMENTOS_INICIAIS = (
    "Administração",
    "Comunicação",
    "Suporte",
    "Tecnologia da Informação",
)


def upgrade() -> None:
    bind = op.get_bind()
    departamentos = sa.table(
        "departamentos",
        sa.column("nome", sa.String()),
        sa.column("limite_simultaneo", sa.Integer()),
        sa.column("criado_em", sa.DateTime()),
    )
    existentes = {
        nome.strip().lower()
        for nome, in bind.execute(sa.text("SELECT nome FROM departamentos"))
        if nome
    }
    agora = datetime.now(UTC).replace(tzinfo=None)
    op.bulk_insert(
        departamentos,
        [
            {
                "nome": nome,
                "limite_simultaneo": 2,
                "criado_em": agora,
            }
            for nome in DEPARTAMENTOS_INICIAIS
            if nome.lower() not in existentes
        ],
    )


def downgrade() -> None:
    # A carga inicial pode passar a ter usuarios vinculados. Preservar os
    # registros evita perda de dados ou quebra de chaves estrangeiras.
    pass
