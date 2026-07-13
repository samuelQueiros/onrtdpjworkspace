"""add second emergency phone

Revision ID: 20260713_0006
Revises: 20260712_0005
Create Date: 2026-07-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0006"
down_revision: Union[str, None] = "20260712_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "telefone_emergencia_2" not in columns:
        op.add_column("users", sa.Column("telefone_emergencia_2", sa.String(), nullable=True))


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "telefone_emergencia_2" in columns:
        op.drop_column("users", "telefone_emergencia_2")
