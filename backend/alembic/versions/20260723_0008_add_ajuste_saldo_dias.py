"""add manual balance override field

Revision ID: 20260723_0008
Revises: 20260713_0007
Create Date: 2026-07-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260723_0008"
down_revision: Union[str, None] = "20260713_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "saldo_manual_dias" not in columns:
        op.add_column(
            "users",
            sa.Column("saldo_manual_dias", sa.Integer(), nullable=True),
        )


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "saldo_manual_dias" in columns:
        op.drop_column("users", "saldo_manual_dias")
