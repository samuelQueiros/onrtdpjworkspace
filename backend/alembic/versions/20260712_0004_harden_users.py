"""harden users and sensitive data

Revision ID: 20260712_0004
Revises: 20260712_0003
Create Date: 2026-07-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.crypto import criptografar_dado_sensivel

revision: str = "20260712_0004"
down_revision: Union[str, None] = "20260712_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}

    if "ativo" not in columns:
        op.add_column("users", sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()))
    if "cargo_id" not in columns:
        op.add_column("users", sa.Column("cargo_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_users_cargo_id", "users", "cargos", ["cargo_id"], ["id"], ondelete="SET NULL")

    if "cargo" in columns:
        bind.execute(sa.text("""
            UPDATE users
               SET cargo_id = cargos.id
              FROM cargos
             WHERE users.cargo = cargos.nome
        """))
        op.drop_column("users", "cargo")

    rows = bind.execute(sa.text("SELECT id, dados_bancarios FROM users WHERE dados_bancarios IS NOT NULL")).all()
    for user_id, valor in rows:
        if valor and not valor.startswith("sensitive:"):
            bind.execute(
                sa.text("UPDATE users SET dados_bancarios = :valor WHERE id = :id"),
                {"valor": criptografar_dado_sensivel(valor), "id": user_id},
            )


def downgrade() -> None:
    op.add_column("users", sa.Column("cargo", sa.String(), nullable=True))
    op.execute("UPDATE users SET cargo = cargos.nome FROM cargos WHERE users.cargo_id = cargos.id")
    op.drop_constraint("fk_users_cargo_id", "users", type_="foreignkey")
    op.drop_column("users", "cargo_id")
    op.drop_column("users", "ativo")
