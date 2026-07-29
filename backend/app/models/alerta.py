from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Alerta(Base):
    __tablename__ = "alertas"
    __table_args__ = (
        UniqueConstraint("ferias_id", "tipo", name="uq_alertas_ferias_tipo"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    ferias_id = Column(Integer, ForeignKey("ferias.id", ondelete="CASCADE"), nullable=True)
    tipo = Column(String, nullable=False)  # "contabilidade_4dias"
    mensagem = Column(String, nullable=False)
    lido = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    ferias = relationship("Ferias")
