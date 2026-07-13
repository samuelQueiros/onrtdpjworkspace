"""add colaborador fields

Revision ID: 20260712_0002
Revises: 20260704_0001
Create Date: 2026-07-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0002"
down_revision: Union[str, None] = "20260704_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    for name in ("telefone", "telefone_emergencia", "endereco", "dados_bancarios", "cargo"):
        if name not in existing:
            op.add_column("users", sa.Column(name, sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "cargo")
    op.drop_column("users", "dados_bancarios")
    op.drop_column("users", "endereco")
    op.drop_column("users", "telefone_emergencia")
    op.drop_column("users", "telefone")
