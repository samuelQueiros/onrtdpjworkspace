"""adiciona constraints e indices das tabelas centrais

Revision ID: 20260731_0021
Revises: 20260731_0020
"""

from alembic import op


revision = "20260731_0021"
down_revision = "20260731_0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE ferias SET status = 'aprovada' WHERE status IS NULL")
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
    op.execute("UPDATE users SET dias_totais = 30 WHERE dias_totais IS NULL")
    op.alter_column("ferias", "status", nullable=False)
    op.alter_column("users", "role", nullable=False)
    op.alter_column("users", "dias_totais", nullable=False)
    op.create_check_constraint(
        "ck_ferias_periodo_valido",
        "ferias",
        "data_fim >= data_inicio",
    )
    op.create_check_constraint(
        "ck_ferias_dias_positivos",
        "ferias",
        "dias_usados > 0",
    )
    op.create_check_constraint(
        "ck_ferias_status_valido",
        "ferias",
        "status IN ('pendente', 'aprovada', 'rejeitada')",
    )
    op.create_check_constraint(
        "ck_users_role_valida",
        "users",
        "role IN ('user', 'admin')",
    )
    op.create_check_constraint(
        "ck_users_dias_totais_positivos",
        "users",
        "dias_totais > 0",
    )
    op.create_index(
        "ix_ferias_user_status_data",
        "ferias",
        ["user_id", "status", "data_inicio"],
    )
    op.create_index(
        "ix_ferias_status_periodo",
        "ferias",
        ["status", "data_inicio", "data_fim"],
    )
    op.create_index(
        "ix_logs_criado_em_id",
        "logs",
        ["criado_em", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_logs_criado_em_id", table_name="logs")
    op.drop_index("ix_ferias_status_periodo", table_name="ferias")
    op.drop_index("ix_ferias_user_status_data", table_name="ferias")
    op.drop_constraint("ck_users_dias_totais_positivos", "users", type_="check")
    op.drop_constraint("ck_users_role_valida", "users", type_="check")
    op.drop_constraint("ck_ferias_status_valido", "ferias", type_="check")
    op.drop_constraint("ck_ferias_dias_positivos", "ferias", type_="check")
    op.drop_constraint("ck_ferias_periodo_valido", "ferias", type_="check")
    op.alter_column("users", "dias_totais", nullable=True)
    op.alter_column("users", "role", nullable=True)
    op.alter_column("ferias", "status", nullable=True)
