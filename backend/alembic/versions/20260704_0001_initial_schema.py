"""initial schema

Revision ID: 20260704_0001
Revises:
Create Date: 2026-07-04
"""

from typing import Sequence, Union

from alembic import op

from app.schema_20260704 import metadata

revision: str = "20260704_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    metadata.create_all(bind=bind)

    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE documentos ADD COLUMN IF NOT EXISTS caminho_arquivo VARCHAR")
        op.execute("ALTER TABLE documentos ADD COLUMN IF NOT EXISTS caminho_enviado VARCHAR")
        op.execute("DELETE FROM documentos WHERE caminho_arquivo IS NULL")
        op.execute("ALTER TABLE documentos DROP COLUMN IF EXISTS conteudo")
        op.execute("ALTER TABLE documentos ALTER COLUMN caminho_arquivo SET NOT NULL")
        op.execute("ALTER TABLE documentos ALTER COLUMN caminho_enviado DROP NOT NULL")


def downgrade() -> None:
    metadata.drop_all(bind=op.get_bind())
