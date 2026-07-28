"""encrypt emergency phone numbers

Revision ID: 20260728_0011
Revises: 20260728_0010
"""

import base64
import hashlib
import os

import sqlalchemy as sa
from alembic import op
from cryptography.fernet import Fernet

revision = "20260728_0011"
down_revision = "20260728_0010"
branch_labels = None
depends_on = None

PREFIX = "sensitive:"


def _fernet() -> Fernet:
    secret = os.getenv("CREDENTIALS_ENCRYPTION_KEY")
    if not secret:
        raise RuntimeError("CREDENTIALS_ENCRYPTION_KEY e obrigatoria para migrar telefones")
    chave = base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())
    return Fernet(chave)


def upgrade() -> None:
    bind = op.get_bind()
    cipher = _fernet()
    rows = bind.execute(
        sa.text(
            "SELECT id, telefone_emergencia, telefone_emergencia_2 "
            "FROM users WHERE telefone_emergencia IS NOT NULL "
            "OR telefone_emergencia_2 IS NOT NULL"
        )
    ).mappings()
    for row in rows:
        valores = {}
        for campo in ("telefone_emergencia", "telefone_emergencia_2"):
            valor = row[campo]
            if valor and not valor.startswith(PREFIX):
                token = cipher.encrypt(valor.encode("utf-8")).decode("utf-8")
                valores[campo] = f"{PREFIX}{token}"
        if valores:
            bind.execute(
                sa.text(
                    "UPDATE users SET "
                    "telefone_emergencia = COALESCE(:telefone_emergencia, telefone_emergencia), "
                    "telefone_emergencia_2 = COALESCE(:telefone_emergencia_2, telefone_emergencia_2) "
                    "WHERE id = :id"
                ),
                {
                    "id": row["id"],
                    "telefone_emergencia": valores.get("telefone_emergencia"),
                    "telefone_emergencia_2": valores.get("telefone_emergencia_2"),
                },
            )


def downgrade() -> None:
    # Criptografia em repouso não deve ser removida em um downgrade estrutural.
    pass
