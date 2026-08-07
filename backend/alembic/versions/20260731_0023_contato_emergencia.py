"""adiciona nome e grau de parentesco ao contato de emergencia

Revision ID: 20260731_0023
Revises: 20260731_0022
"""

import base64
import hashlib
import json
import os

import sqlalchemy as sa
from alembic import op
from cryptography.fernet import Fernet, InvalidToken

revision = "20260731_0023"
down_revision = "20260731_0022"
branch_labels = None
depends_on = None

PREFIX = "sensitive:"


def _fernet() -> Fernet:
    secret = os.getenv("CREDENTIALS_ENCRYPTION_KEY")
    if not secret:
        raise RuntimeError("CREDENTIALS_ENCRYPTION_KEY e obrigatoria para migrar contatos de emergencia")
    chave = base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())
    return Fernet(chave)


def _decifrar(cipher: Fernet, valor: str | None) -> str | None:
    if not valor:
        return None
    if not valor.startswith(PREFIX):
        return valor
    try:
        return cipher.decrypt(valor.removeprefix(PREFIX).encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return None


def upgrade() -> None:
    op.add_column("users", sa.Column("contato_emergencia_1", sa.String(), nullable=True))
    op.add_column("users", sa.Column("contato_emergencia_2", sa.String(), nullable=True))

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
        for campo_antigo, campo_novo in (
            ("telefone_emergencia", "contato_emergencia_1"),
            ("telefone_emergencia_2", "contato_emergencia_2"),
        ):
            telefone = _decifrar(cipher, row[campo_antigo])
            if telefone:
                conteudo = json.dumps(
                    {"telefone": telefone, "nome": "", "grau_parentesco": ""},
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                token = cipher.encrypt(conteudo.encode("utf-8")).decode("utf-8")
                valores[campo_novo] = f"{PREFIX}{token}"
        if valores:
            bind.execute(
                sa.text(
                    "UPDATE users SET "
                    "contato_emergencia_1 = COALESCE(:contato_emergencia_1, contato_emergencia_1), "
                    "contato_emergencia_2 = COALESCE(:contato_emergencia_2, contato_emergencia_2) "
                    "WHERE id = :id"
                ),
                {
                    "id": row["id"],
                    "contato_emergencia_1": valores.get("contato_emergencia_1"),
                    "contato_emergencia_2": valores.get("contato_emergencia_2"),
                },
            )

    op.drop_column("users", "telefone_emergencia")
    op.drop_column("users", "telefone_emergencia_2")


def downgrade() -> None:
    op.add_column("users", sa.Column("telefone_emergencia", sa.String(), nullable=True))
    op.add_column("users", sa.Column("telefone_emergencia_2", sa.String(), nullable=True))

    bind = op.get_bind()
    cipher = _fernet()
    rows = bind.execute(
        sa.text(
            "SELECT id, contato_emergencia_1, contato_emergencia_2 "
            "FROM users WHERE contato_emergencia_1 IS NOT NULL "
            "OR contato_emergencia_2 IS NOT NULL"
        )
    ).mappings()
    for row in rows:
        valores = {}
        for campo_novo, campo_antigo in (
            ("contato_emergencia_1", "telefone_emergencia"),
            ("contato_emergencia_2", "telefone_emergencia_2"),
        ):
            conteudo = _decifrar(cipher, row[campo_novo])
            if not conteudo:
                continue
            try:
                telefone = json.loads(conteudo).get("telefone")
            except (json.JSONDecodeError, AttributeError):
                telefone = conteudo
            if telefone:
                token = cipher.encrypt(telefone.encode("utf-8")).decode("utf-8")
                valores[campo_antigo] = f"{PREFIX}{token}"
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

    op.drop_column("users", "contato_emergencia_1")
    op.drop_column("users", "contato_emergencia_2")
