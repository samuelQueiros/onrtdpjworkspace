"""adiciona destino explicito aos documentos

Revision ID: 20260728_0010
Revises: 20260726_0009
"""

from alembic import op
import sqlalchemy as sa


revision = "20260728_0010"
down_revision = "20260726_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documentos",
        sa.Column("destino_tipo", sa.String(), server_default="usuario", nullable=False),
    )
    op.add_column(
        "documentos",
        sa.Column("destinatario_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_documentos_destinatario_id",
        "documentos",
        "users",
        ["destinatario_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "ck_documentos_destino_tipo",
        "documentos",
        "destino_tipo IN ('usuario', 'administracao')",
    )

    op.execute(
        """
        UPDATE documentos AS d
        SET destino_tipo = CASE
                WHEN d.tipo IN ('contracheque', 'termo_equipamentos') THEN 'usuario'
                WHEN EXISTS (
                    SELECT 1 FROM users AS u
                    WHERE u.id = d.criado_por_id AND u.role = 'admin'
                ) THEN 'usuario'
                ELSE 'administracao'
            END,
            destinatario_id = CASE
                WHEN d.tipo IN ('contracheque', 'termo_equipamentos') THEN d.user_id
                WHEN EXISTS (
                    SELECT 1 FROM users AS u
                    WHERE u.id = d.criado_por_id AND u.role = 'admin'
                ) THEN d.user_id
                ELSE NULL
            END
        """
    )
    op.alter_column("documentos", "destino_tipo", server_default=None)
    op.create_index(
        "ix_documentos_destino_destinatario",
        "documentos",
        ["destino_tipo", "destinatario_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_documentos_destino_destinatario", table_name="documentos")
    op.drop_constraint("ck_documentos_destino_tipo", "documentos", type_="check")
    op.drop_constraint("fk_documentos_destinatario_id", "documentos", type_="foreignkey")
    op.drop_column("documentos", "destinatario_id")
    op.drop_column("documentos", "destino_tipo")
