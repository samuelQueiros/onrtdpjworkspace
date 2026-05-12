from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Ferias(Base):
    __tablename__ = "ferias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    dias_usados = Column(Integer, nullable=False)
    # pendente = aguardando aprovação admin; aprovada = ativa; rejeitada = negada
    status = Column(String, default="aprovada")
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
