"""cria configuracao, envios e envio_eventos (lembrete automatico de ferias por e-mail)

Revision ID: 20260807_0024
Revises: 20260731_0023
"""

import sqlalchemy as sa
from alembic import op


revision = "20260807_0024"
down_revision = "20260731_0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "configuracao",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email_destinatario", sa.String(length=255), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_configuracao_singleton"),
        sa.PrimaryKeyConstraint("id", name="pk_configuracao"),
    )

    op.create_table(
        "envios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alerta_id", sa.Integer(), nullable=False),
        sa.Column("colaborador_nome_snapshot", sa.String(length=150), nullable=False),
        sa.Column("periodo_ferias_snapshot", sa.String(length=60), nullable=False),
        sa.Column("destinatario_email_snapshot", sa.String(length=255), nullable=False),
        sa.Column("message_id", sa.String(length=255), nullable=False),
        sa.Column("token_rastreio", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("erro_codigo", sa.String(length=10), nullable=True),
        sa.Column("erro_mensagem", sa.Text(), nullable=True),
        sa.Column("tentativas_verificacao", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enviado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prazo_limite", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ultima_verificacao_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("respondido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resposta_texto", sa.Text(), nullable=True),
        sa.Column("resposta_bruta", sa.Text(), nullable=True),
        sa.Column("enviado_por_id", sa.Integer(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('enviado','monitorando','erro_definitivo','respondido','sem_retorno')",
            name="ck_envios_status",
        ),
        sa.ForeignKeyConstraint(
            ["alerta_id"],
            ["alertas.id"],
            name="fk_envios_alerta_id",
            # RESTRICT: um alerta/ferias com e-mail ja enviado nao pode ser excluido fisicamente
            # sem perder a trilha de auditoria de um envio que ja aconteceu de verdade.
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["enviado_por_id"],
            ["users.id"],
            name="fk_envios_enviado_por_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_envios"),
        # UNIQUE em alerta_id garante no maximo um envio por alerta (idempotencia do botao "Enviar").
        sa.UniqueConstraint("alerta_id", name="uq_envios_alerta_id"),
        sa.UniqueConstraint("message_id", name="uq_envios_message_id"),
        sa.UniqueConstraint("token_rastreio", name="uq_envios_token_rastreio"),
    )
    op.create_index("ix_envios_status", "envios", ["status"], unique=False)

    op.create_table(
        "envio_eventos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("envio_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("status_anterior", sa.String(length=30), nullable=True),
        sa.Column("status_novo", sa.String(length=30), nullable=True),
        sa.Column("detalhes", sa.Text(), nullable=True),
        sa.Column("criado_por_id", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "tipo IN ('envio_criado','verificacao_realizada','bounce_temporario',"
            "'bounce_definitivo','resposta_detectada','prazo_estourado','erro_verificacao')",
            name="ck_envio_eventos_tipo",
        ),
        sa.ForeignKeyConstraint(
            ["envio_id"],
            ["envios.id"],
            name="fk_envio_eventos_envio_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["criado_por_id"],
            ["users.id"],
            name="fk_envio_eventos_criado_por_id",
            # nullable: transicoes disparadas pelo job de monitoramento (bounce, resposta,
            # prazo estourado) nao tem um usuario associado, diferente de equipamento_eventos/
            # solicitacao_equipamento_eventos, onde criado_por_id e sempre obrigatorio.
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_envio_eventos"),
    )
    op.create_index(
        "ix_envio_eventos_envio_data",
        "envio_eventos",
        ["envio_id", "criado_em"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_envio_eventos_envio_data", table_name="envio_eventos")
    op.drop_table("envio_eventos")
    op.drop_index("ix_envios_status", table_name="envios")
    op.drop_table("envios")
    op.drop_table("configuracao")
