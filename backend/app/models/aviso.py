from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Aviso(Base):
    __tablename__ = "avisos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    conteudo = Column(String, nullable=False)
    fixado = Column(Boolean, default=False)
    data_expiracao = Column(Date, nullable=True)
    criado_por_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    criado_por = relationship("User", foreign_keys=[criado_por_id])
