"""Frozen schema snapshot used only by the initial Alembic revision."""

import sqlalchemy as sa

metadata = sa.MetaData()

departamentos = sa.Table(
    "departamentos", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("nome", sa.String, nullable=False, unique=True),
    sa.Column("limite_simultaneo", sa.Integer),
    sa.Column("criado_em", sa.DateTime),
)
users = sa.Table(
    "users", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("nome", sa.String, nullable=False),
    sa.Column("email", sa.String, nullable=False, unique=True),
    sa.Column("senha_hash", sa.String, nullable=False),
    sa.Column("role", sa.String),
    sa.Column("dias_totais", sa.Integer),
    sa.Column("departamento_id", sa.Integer, sa.ForeignKey("departamentos.id")),
    sa.Column("data_admissao", sa.Date),
    sa.Column("data_aniversario", sa.Date),
    sa.Column("cor", sa.String),
    sa.Column("criado_em", sa.DateTime),
)
ferias = sa.Table(
    "ferias", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
    sa.Column("data_inicio", sa.Date, nullable=False),
    sa.Column("data_fim", sa.Date, nullable=False),
    sa.Column("dias_usados", sa.Integer, nullable=False),
    sa.Column("status", sa.String),
    sa.Column("ferias_acordo", sa.Boolean),
    sa.Column("motivo_rejeicao", sa.String),
    sa.Column("criado_em", sa.DateTime),
    sa.Column("aprovado_por_id", sa.Integer, sa.ForeignKey("users.id")),
    sa.Column("aprovado_em", sa.DateTime),
    sa.Column("rejeitado_por_id", sa.Integer, sa.ForeignKey("users.id")),
    sa.Column("rejeitado_em", sa.DateTime),
)
sa.Table(
    "logs", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
    sa.Column("acao", sa.String, nullable=False),
    sa.Column("detalhes", sa.String),
    sa.Column("criado_em", sa.DateTime),
)
sa.Table(
    "avisos", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("titulo", sa.String, nullable=False),
    sa.Column("conteudo", sa.String, nullable=False),
    sa.Column("fixado", sa.Boolean),
    sa.Column("data_expiracao", sa.Date),
    sa.Column("criado_por_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
    sa.Column("criado_em", sa.DateTime),
)
sa.Table(
    "documentos", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
    sa.Column("tipo", sa.String, nullable=False),
    sa.Column("nome_arquivo", sa.String, nullable=False),
    sa.Column("mime_type", sa.String, nullable=False),
    sa.Column("caminho_arquivo", sa.String, nullable=False),
    sa.Column("caminho_enviado", sa.String),
    sa.Column("tamanho", sa.Integer, nullable=False),
    sa.Column("criado_por_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
    sa.Column("criado_em", sa.DateTime),
)
credenciais = sa.Table(
    "credenciais", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("descricao", sa.String, nullable=False),
    sa.Column("email", sa.String, nullable=False),
    sa.Column("senha", sa.String, nullable=False),
    sa.Column("criado_em", sa.DateTime),
    sa.Column("atualizado_em", sa.DateTime),
)
sa.Table(
    "credencial_usuarios", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("credencial_id", sa.Integer, sa.ForeignKey("credenciais.id", ondelete="CASCADE"), nullable=False),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    sa.Column("criado_em", sa.DateTime),
)
sa.Table(
    "bloqueios_datas", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("data_inicio", sa.Date, nullable=False),
    sa.Column("data_fim", sa.Date, nullable=False),
    sa.Column("motivo", sa.String, nullable=False),
    sa.Column("tipo", sa.String),
    sa.Column("criado_por_id", sa.Integer, sa.ForeignKey("users.id")),
    sa.Column("criado_em", sa.DateTime),
)
sa.Table(
    "alertas", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("ferias_id", sa.Integer, sa.ForeignKey("ferias.id", ondelete="CASCADE")),
    sa.Column("tipo", sa.String, nullable=False),
    sa.Column("mensagem", sa.String, nullable=False),
    sa.Column("lido", sa.Boolean),
    sa.Column("criado_em", sa.DateTime),
)
