"""security and integrity constraints

Revision ID: 20260728_0012
Revises: 20260728_0011
"""

import sqlalchemy as sa
from alembic import op

revision = "20260728_0012"
down_revision = "20260728_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "must_change_password",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    bind = op.get_bind()
    duplicados = bind.execute(
        sa.text(
            "SELECT lower(trim(email)) AS email_normalizado, count(*) "
            "FROM users GROUP BY lower(trim(email)) HAVING count(*) > 1"
        )
    ).first()
    if duplicados:
        raise RuntimeError(
            "Existem usuarios com e-mails iguais variando apenas maiusculas/minusculas. "
            "Corrija-os antes de aplicar esta migracao."
        )
    bind.execute(sa.text("UPDATE users SET email = lower(trim(email))"))
    op.create_index(
        "uq_users_email_normalizado",
        "users",
        [sa.text("lower(email)")],
        unique=True,
    )

    bind.execute(
        sa.text(
            "DELETE FROM credencial_usuarios a USING credencial_usuarios b "
            "WHERE a.id > b.id AND a.credencial_id = b.credencial_id "
            "AND a.user_id = b.user_id"
        )
    )
    op.create_unique_constraint(
        "uq_credencial_usuario",
        "credencial_usuarios",
        ["credencial_id", "user_id"],
    )

    bind.execute(
        sa.text(
            "DELETE FROM alertas a USING alertas b "
            "WHERE a.id > b.id AND a.ferias_id = b.ferias_id "
            "AND a.tipo = b.tipo"
        )
    )
    op.create_unique_constraint(
        "uq_alertas_ferias_tipo",
        "alertas",
        ["ferias_id", "tipo"],
    )

    bind.execute(
        sa.text(
            "UPDATE solicitacoes_equipamentos "
            "SET status = 'aguardando_entrega' WHERE status = 'aprovada'"
        )
    )
    op.drop_constraint(
        "ck_solicitacoes_equipamentos_status",
        "solicitacoes_equipamentos",
        type_="check",
    )
    op.create_check_constraint(
        "ck_solicitacoes_equipamentos_status",
        "solicitacoes_equipamentos",
        "status IN ('pendente','rejeitada','cancelada','aguardando_entrega',"
        "'aguardando_aceite','aceite_registrado_aguardando_documento',"
        "'entregue','devolvida')",
    )
    op.alter_column(
        "users",
        "must_change_password",
        server_default=sa.true(),
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_solicitacoes_equipamentos_status",
        "solicitacoes_equipamentos",
        type_="check",
    )
    op.create_check_constraint(
        "ck_solicitacoes_equipamentos_status",
        "solicitacoes_equipamentos",
        "status IN ('pendente','aprovada','rejeitada','cancelada',"
        "'aguardando_entrega','aguardando_aceite',"
        "'aceite_registrado_aguardando_documento','entregue','devolvida')",
    )
    op.drop_constraint("uq_alertas_ferias_tipo", "alertas", type_="unique")
    op.drop_constraint("uq_credencial_usuario", "credencial_usuarios", type_="unique")
    op.drop_index("uq_users_email_normalizado", table_name="users")
    op.drop_column("users", "must_change_password")
