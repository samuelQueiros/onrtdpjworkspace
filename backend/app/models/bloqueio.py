from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class BloqueioData(Base):
    __tablename__ = "bloqueios_datas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    motivo = Column(String, nullable=False)
    tipo = Column(String, default="bloqueio")  # "bloqueio" ou "recesso"
    criado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    criado_por = relationship("User")
