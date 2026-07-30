from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, String, Text

from app.database import Base


def agora_utc() -> datetime:
    return datetime.now(UTC)


CAMPOS_HISTORICO_COLABORADOR = ("cargo", "departamento", "valor_beneficios")
TIPOS_ALTERACAO = ("real", "correcao")


class HistoricoColaborador(Base):
    __tablename__ = "historico_colaborador"
    __table_args__ = (
        CheckConstraint(
            "campo IN ('cargo','departamento','valor_beneficios')",
            name="ck_historico_colaborador_campo",
        ),
        CheckConstraint(
            "tipo_alteracao IN ('real','correcao')",
            name="ck_historico_colaborador_tipo_alteracao",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    campo = Column(String(30), nullable=False)
    # None na primeira atribuicao (cadastro inicial), preenchido daí em diante.
    valor_anterior_criptografado = Column(Text, nullable=True)
    valor_novo_criptografado = Column(Text, nullable=False)
    # "real": evento de carreira de verdade (entra na linha do tempo/estatisticas).
    # "correcao": conserta um valor cadastrado errado, mantido para auditoria
    # mas nao deve ser interpretado como uma mudanca real.
    tipo_alteracao = Column(String(20), nullable=False, server_default="real")
    motivo = Column(Text, nullable=True)
    data_vigencia = Column(Date, nullable=False)
    criado_por_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
