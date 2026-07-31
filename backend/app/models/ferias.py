from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Ferias(Base):
    __tablename__ = "ferias"
    __table_args__ = (
        CheckConstraint("data_fim >= data_inicio", name="ck_ferias_periodo_valido"),
        CheckConstraint("dias_usados > 0", name="ck_ferias_dias_positivos"),
        CheckConstraint(
            "status IN ('pendente', 'aprovada', 'rejeitada')",
            name="ck_ferias_status_valido",
        ),
        Index("ix_ferias_user_status_data", "user_id", "status", "data_inicio"),
        Index("ix_ferias_status_periodo", "status", "data_inicio", "data_fim"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    dias_usados = Column(Integer, nullable=False)
    # pendente = aguardando aprovação admin; aprovada = ativa; rejeitada = negada
    status = Column(String, nullable=False, default="aprovada")
    ferias_acordo = Column(Boolean, default=False)  # não desconta saldo
    motivo_rejeicao = Column(String, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Histórico de aprovação/rejeição
    aprovado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    aprovado_em = Column(DateTime, nullable=True)
    rejeitado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejeitado_em = Column(DateTime, nullable=True)

    usuario = relationship("User", back_populates="ferias", foreign_keys=[user_id])
    aprovado_por = relationship("User", foreign_keys=[aprovado_por_id])
    rejeitado_por = relationship("User", foreign_keys=[rejeitado_por_id])
