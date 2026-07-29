"""cria fichas admissionais dos colaboradores

Revision ID: 20260729_0016
Revises: 20260729_0015
"""

import sqlalchemy as sa
from alembic import op


revision = "20260729_0016"
down_revision = "20260729_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fichas_admissionais",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("local_nascimento_criptografado", sa.Text(), nullable=True),
        sa.Column("uf_nascimento", sa.String(length=2), nullable=True),
        sa.Column("nacionalidade_criptografada", sa.Text(), nullable=True),
        sa.Column("sexo", sa.String(length=20), nullable=True),
        sa.Column("nome_mae_criptografado", sa.Text(), nullable=True),
        sa.Column("nome_pai_criptografado", sa.Text(), nullable=True),
        sa.Column("pis_numero_criptografado", sa.Text(), nullable=True),
        sa.Column("pis_emissao", sa.Date(), nullable=True),
        sa.Column("rg_numero_criptografado", sa.Text(), nullable=True),
        sa.Column("rg_emissao", sa.Date(), nullable=True),
        sa.Column("rg_orgao_emissor_criptografado", sa.Text(), nullable=True),
        sa.Column("ctps_numero_criptografado", sa.Text(), nullable=True),
        sa.Column("ctps_serie_criptografada", sa.Text(), nullable=True),
        sa.Column("ctps_validade", sa.Date(), nullable=True),
        sa.Column("ctps_uf", sa.String(length=2), nullable=True),
        sa.Column("ctps_emissao", sa.Date(), nullable=True),
        sa.Column("telefone_alternativo_criptografado", sa.Text(), nullable=True),
        sa.Column("email_alternativo_criptografado", sa.Text(), nullable=True),
        sa.Column("endereco_uf", sa.String(length=2), nullable=True),
        sa.Column("estado_civil", sa.String(length=30), nullable=True),
        sa.Column("nome_conjuge_criptografado", sa.Text(), nullable=True),
        sa.Column("grau_instrucao", sa.String(length=120), nullable=True),
        sa.Column("salario_criptografado", sa.Text(), nullable=True),
        sa.Column("horario_trabalho_criptografado", sa.Text(), nullable=True),
        sa.Column("dias_semana_criptografados", sa.Text(), nullable=True),
        sa.Column("vale_transporte_criptografado", sa.Text(), nullable=True),
        sa.Column("beneficios_criptografados", sa.Text(), nullable=True),
        sa.Column("valor_beneficios_criptografado", sa.Text(), nullable=True),
        sa.Column("contrato_experiencia_dias", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="rascunho"),
        sa.Column("criado_por_id", sa.Integer(), nullable=True),
        sa.Column("atualizado_por_id", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('rascunho','completa')",
            name="ck_fichas_admissionais_status",
        ),
        sa.CheckConstraint(
            "sexo IS NULL OR sexo IN ('feminino','masculino','outro','nao_informado')",
            name="ck_fichas_admissionais_sexo",
        ),
        sa.CheckConstraint(
            "estado_civil IS NULL OR estado_civil IN "
            "('solteiro','casado','divorciado','viuvo','separado','uniao_estavel','outro')",
            name="ck_fichas_admissionais_estado_civil",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criado_por_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["atualizado_por_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("user_id", name="uq_fichas_admissionais_user_id"),
    )


def downgrade() -> None:
    op.drop_table("fichas_admissionais")
