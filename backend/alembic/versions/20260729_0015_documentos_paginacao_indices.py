"""adiciona indices para paginacao de documentos

Revision ID: 20260729_0015
Revises: 20260729_0014
"""

from alembic import op


revision = "20260729_0015"
down_revision = "20260729_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(
        "ix_documentos_destino_destinatario",
        table_name="documentos",
    )
    op.create_index(
        "ix_documentos_destino_destinatario",
        "documentos",
        ["destino_tipo", "destinatario_id", "criado_em"],
    )
    op.create_index(
        "ix_documentos_destino_usuario_criado_em",
        "documentos",
        ["destino_tipo", "user_id", "criado_em"],
    )
    op.create_index(
        "ix_documentos_criador_criado_em",
        "documentos",
        ["criado_por_id", "criado_em"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_documentos_criador_criado_em",
        table_name="documentos",
    )
    op.drop_index(
        "ix_documentos_destino_usuario_criado_em",
        table_name="documentos",
    )
    op.drop_index(
        "ix_documentos_destino_destinatario",
        table_name="documentos",
    )
    op.create_index(
        "ix_documentos_destino_destinatario",
        "documentos",
        ["destino_tipo", "destinatario_id"],
    )
