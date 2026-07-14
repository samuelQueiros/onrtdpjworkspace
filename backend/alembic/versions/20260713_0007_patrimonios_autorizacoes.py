"""create assets and equipment authorization module

Revision ID: 20260713_0007
Revises: 20260713_0006
Create Date: 2026-07-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260713_0007"
down_revision: Union[str, None] = "20260713_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("cpf_criptografado", sa.String(), nullable=True))
    op.add_column("users", sa.Column("cpf_hash", sa.String(length=64), nullable=True))
    op.create_unique_constraint("uq_users_cpf_hash", "users", ["cpf_hash"])

    op.create_table(
        "equipamentos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("numero_patrimonio", sa.String(length=80), nullable=True),
        sa.Column("numero_serie", sa.String(length=120), nullable=True),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("marca", sa.String(length=100), nullable=False),
        sa.Column("modelo", sa.String(length=120), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("estado_conservacao", sa.String(length=300), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "tipo IN ('notebook','desktop','monitor','mouse','teclado','headset','dock_station',"
            "'carregador','cabo_energia','adaptador','outro')",
            name="ck_equipamentos_tipo",
        ),
        sa.CheckConstraint(
            "status IN ('disponivel','vinculado','reservado','manutencao','baixado')",
            name="ck_equipamentos_status",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_equipamentos"),
        sa.UniqueConstraint("numero_patrimonio", name="uq_equipamentos_numero_patrimonio"),
        sa.UniqueConstraint("numero_serie", name="uq_equipamentos_numero_serie"),
    )
    op.create_index(
        "ix_equipamentos_busca",
        "equipamentos",
        ["tipo", "status", "ativo"],
        unique=False,
    )

    op.create_table(
        "equipamento_vinculos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("equipamento_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("vinculado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("desvinculado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("vinculado_por_id", sa.Integer(), nullable=False),
        sa.Column("desvinculado_por_id", sa.Integer(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("maquina_principal", sa.Boolean(), nullable=False),
        sa.Column("excecao_maquina_principal", sa.Boolean(), nullable=False),
        sa.Column("justificativa_excecao", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["equipamento_id"],
            ["equipamentos.id"],
            name="fk_equipamento_vinculos_equipamento_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_equipamento_vinculos_user_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vinculado_por_id"],
            ["users.id"],
            name="fk_equipamento_vinculos_vinculado_por_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["desvinculado_por_id"],
            ["users.id"],
            name="fk_equipamento_vinculos_desvinculado_por_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_equipamento_vinculos"),
    )
    op.create_index(
        "ix_equipamento_vinculos_user_ativo",
        "equipamento_vinculos",
        ["user_id", "desvinculado_em"],
        unique=False,
    )
    op.create_index(
        "uq_equipamento_vinculo_ativo",
        "equipamento_vinculos",
        ["equipamento_id"],
        unique=True,
        postgresql_where=sa.text("desvinculado_em IS NULL"),
    )
    op.create_index(
        "uq_usuario_maquina_principal_padrao_ativa",
        "equipamento_vinculos",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text(
            "desvinculado_em IS NULL AND maquina_principal IS TRUE "
            "AND excecao_maquina_principal IS FALSE"
        ),
    )

    op.create_table(
        "equipamento_eventos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("equipamento_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("status_anterior", sa.String(length=30), nullable=True),
        sa.Column("status_novo", sa.String(length=30), nullable=True),
        sa.Column("estado_conservacao", sa.String(length=300), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("criado_por_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["equipamento_id"],
            ["equipamentos.id"],
            name="fk_equipamento_eventos_equipamento_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["criado_por_id"],
            ["users.id"],
            name="fk_equipamento_eventos_criado_por_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_equipamento_eventos"),
    )
    op.create_index(
        "ix_equipamento_eventos_equipamento_data",
        "equipamento_eventos",
        ["equipamento_id", "criado_em"],
        unique=False,
    )

    op.create_table(
        "termo_equipamento_versoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo", sa.String(length=30), nullable=False),
        sa.Column("vigente_desde", sa.DateTime(timezone=True), nullable=False),
        sa.Column("conteudo_hash", sa.String(length=64), nullable=False),
        sa.Column("clausulas", sa.Text(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_termo_equipamento_versoes"),
        sa.UniqueConstraint("codigo", name="uq_termo_equipamento_versoes_codigo"),
    )

    op.create_table(
        "solicitacoes_equipamentos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tipo_solicitacao", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("nome_colaborador_snapshot", sa.String(length=150), nullable=False),
        sa.Column("cpf_snapshot_criptografado", sa.Text(), nullable=False),
        sa.Column("cargo_snapshot", sa.String(length=120), nullable=False),
        sa.Column("departamento_snapshot", sa.String(length=150), nullable=False),
        sa.Column("aprovado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("aprovado_por_id", sa.Integer(), nullable=True),
        sa.Column("rejeitado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejeitado_por_id", sa.Integer(), nullable=True),
        sa.Column("motivo_rejeicao", sa.Text(), nullable=True),
        sa.Column("cancelado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelado_por_id", sa.Integer(), nullable=True),
        sa.Column("motivo_cancelamento", sa.Text(), nullable=True),
        sa.Column("entregue_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("entregue_por_id", sa.Integer(), nullable=True),
        sa.Column("responsavel_entrega_nome", sa.String(length=150), nullable=True),
        sa.Column("responsavel_entrega_cargo", sa.String(length=120), nullable=True),
        sa.Column("local_entrega", sa.String(length=180), nullable=True),
        sa.Column("aceito_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("aceite_ip", sa.String(length=64), nullable=True),
        sa.Column("aceite_request_id", sa.String(length=80), nullable=True),
        sa.Column("local_aceite", sa.String(length=180), nullable=True),
        sa.Column("aceite_declaracao", sa.Boolean(), nullable=False),
        sa.Column("termo_versao_id", sa.Integer(), nullable=True),
        sa.Column("termo_html_snapshot_criptografado", sa.Text(), nullable=True),
        sa.Column("documento_id", sa.Integer(), nullable=True),
        sa.Column("documento_hash", sa.String(length=64), nullable=True),
        sa.Column("documento_status", sa.String(length=30), nullable=False),
        sa.Column("documento_erro", sa.Text(), nullable=True),
        sa.Column("devolvido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("devolvido_por_id", sa.Integer(), nullable=True),
        sa.Column("recebido_devolucao_por_id", sa.Integer(), nullable=True),
        sa.Column("estado_conservacao_devolucao", sa.String(length=300), nullable=True),
        sa.Column("itens_ausentes_devolucao", sa.Text(), nullable=True),
        sa.Column("observacoes_devolucao", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "tipo_solicitacao IN ('itens_vinculados','item_diferente')",
            name="ck_solicitacoes_equipamentos_tipo",
        ),
        sa.CheckConstraint(
            "status IN ('pendente','aprovada','rejeitada','cancelada','aguardando_entrega',"
            "'aguardando_aceite','aceite_registrado_aguardando_documento','entregue','devolvida')",
            name="ck_solicitacoes_equipamentos_status",
        ),
        sa.CheckConstraint(
            "documento_status IN ('pendente','gerando','gerado','falha')",
            name="ck_solicitacoes_equipamentos_documento_status",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_solicitacoes_equipamentos_user_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["aprovado_por_id"],
            ["users.id"],
            name="fk_solicitacoes_equipamentos_aprovado_por_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["rejeitado_por_id"],
            ["users.id"],
            name="fk_solicitacoes_equipamentos_rejeitado_por_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cancelado_por_id"],
            ["users.id"],
            name="fk_solicitacoes_equipamentos_cancelado_por_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["entregue_por_id"],
            ["users.id"],
            name="fk_solicitacoes_equipamentos_entregue_por_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["devolvido_por_id"],
            ["users.id"],
            name="fk_solicitacoes_equipamentos_devolvido_por_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["recebido_devolucao_por_id"],
            ["users.id"],
            name="fk_solicitacoes_equipamentos_recebido_devolucao_por_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["termo_versao_id"],
            ["termo_equipamento_versoes.id"],
            name="fk_solicitacoes_equipamentos_termo_versao_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["documento_id"],
            ["documentos.id"],
            name="fk_solicitacoes_equipamentos_documento_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_solicitacoes_equipamentos"),
        sa.UniqueConstraint(
            "documento_id",
            name="uq_solicitacoes_equipamentos_documento",
        ),
    )
    op.create_index(
        "ix_solicitacoes_equipamentos_user_status",
        "solicitacoes_equipamentos",
        ["user_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_solicitacoes_equipamentos_status_criado",
        "solicitacoes_equipamentos",
        ["status", "criado_em"],
        unique=False,
    )

    op.create_table(
        "solicitacao_equipamento_itens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("solicitacao_id", sa.Integer(), nullable=False),
        sa.Column("equipamento_id", sa.Integer(), nullable=False),
        sa.Column("status_item", sa.String(length=30), nullable=False),
        sa.Column("motivo_remocao", sa.Text(), nullable=True),
        sa.Column("removido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("removido_por_id", sa.Integer(), nullable=True),
        sa.Column("reservado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reserva_liberada_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("vinculo_criado_entrega_id", sa.Integer(), nullable=True),
        sa.Column("numero_patrimonio_snapshot", sa.String(length=80), nullable=True),
        sa.Column("numero_serie_snapshot", sa.String(length=120), nullable=True),
        sa.Column("tipo_snapshot", sa.String(length=40), nullable=False),
        sa.Column("marca_modelo_snapshot", sa.String(length=240), nullable=False),
        sa.Column("estado_conservacao_snapshot", sa.String(length=300), nullable=False),
        sa.Column("observacoes_snapshot", sa.Text(), nullable=True),
        sa.Column("entregue_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("devolvido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estado_conservacao_devolucao", sa.String(length=300), nullable=True),
        sa.Column("observacoes_devolucao", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["solicitacao_id"],
            ["solicitacoes_equipamentos.id"],
            name="fk_solicitacao_equipamento_itens_solicitacao_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["equipamento_id"],
            ["equipamentos.id"],
            name="fk_solicitacao_equipamento_itens_equipamento_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["removido_por_id"],
            ["users.id"],
            name="fk_solicitacao_equipamento_itens_removido_por_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vinculo_criado_entrega_id"],
            ["equipamento_vinculos.id"],
            name="fk_solicitacao_equipamento_itens_vinculo_criado_entrega_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_solicitacao_equipamento_itens"),
        sa.CheckConstraint(
            "status_item IN ('solicitado','aprovado','removido','entregue','devolvido','ausente')",
            name="ck_solicitacao_equipamento_itens_status",
        ),
        sa.CheckConstraint(
            "reserva_liberada_em IS NULL OR reservado_em IS NOT NULL",
            name="ck_solicitacao_equipamento_itens_reserva",
        ),
        sa.UniqueConstraint(
            "solicitacao_id",
            "equipamento_id",
            name="uq_solicitacao_equipamento_item",
        ),
    )
    op.create_index(
        "ix_solicitacao_equipamento_itens_equipamento",
        "solicitacao_equipamento_itens",
        ["equipamento_id"],
        unique=False,
    )
    op.create_index(
        "uq_solicitacao_item_reserva_ativa",
        "solicitacao_equipamento_itens",
        ["equipamento_id"],
        unique=True,
        postgresql_where=sa.text("reservado_em IS NOT NULL AND reserva_liberada_em IS NULL"),
    )

    op.create_table(
        "solicitacao_equipamento_eventos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("solicitacao_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=60), nullable=False),
        sa.Column("status_anterior", sa.String(length=60), nullable=True),
        sa.Column("status_novo", sa.String(length=60), nullable=True),
        sa.Column("detalhes", sa.Text(), nullable=True),
        sa.Column("criado_por_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["solicitacao_id"],
            ["solicitacoes_equipamentos.id"],
            name="fk_solicitacao_equipamento_eventos_solicitacao_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["criado_por_id"],
            ["users.id"],
            name="fk_solicitacao_equipamento_eventos_criado_por_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_solicitacao_equipamento_eventos"),
    )
    op.create_index(
        "ix_solicitacao_equipamento_eventos_data",
        "solicitacao_equipamento_eventos",
        ["solicitacao_id", "criado_em"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("solicitacao_equipamento_eventos")
    op.drop_table("solicitacao_equipamento_itens")
    op.drop_table("solicitacoes_equipamentos")
    op.drop_table("termo_equipamento_versoes")
    op.drop_table("equipamento_eventos")
    op.drop_table("equipamento_vinculos")
    op.drop_table("equipamentos")

    op.drop_constraint("uq_users_cpf_hash", "users", type_="unique")
    op.drop_column("users", "cpf_hash")
    op.drop_column("users", "cpf_criptografado")
