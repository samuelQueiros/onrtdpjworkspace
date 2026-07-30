from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, String, Text

from app.database import Base


def agora_utc() -> datetime:
    return datetime.now(UTC)


TIPOS_HISTORICO_SALARIAL = ("reajuste", "correcao")


class HistoricoSalarial(Base):
    __tablename__ = "historico_salarial"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('reajuste','correcao')",
            name="ck_historico_salarial_tipo",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    salario_criptografado = Column(Text, nullable=False)
    data_vigencia = Column(Date, nullable=False)
    # "reajuste": conta como aumento real (entra no grafico/estatisticas).
    # "correcao": conserta um valor cadastrado errado, mantido para auditoria
    # mas nao deve ser interpretado como reajuste salarial.
    tipo = Column(String(20), nullable=False, server_default="reajuste")
    motivo = Column(Text, nullable=True)
    criado_por_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
