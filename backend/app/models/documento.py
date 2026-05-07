from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tipo = Column(String, nullable=False)  # "atestado" ou "contracheque"
    nome_arquivo = Column(String, nullable=False)
    mime_type = Column(String, nullable=False, default="application/octet-stream")
    conteudo = Column(LargeBinary, nullable=False)
    tamanho = Column(Integer, nullable=False)
    criado_por_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("User", foreign_keys=[user_id], back_populates="documentos")
    criado_por = relationship("User", foreign_keys=[criado_por_id])
