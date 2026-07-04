from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
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
    caminho_arquivo = Column(String, nullable=False)
    caminho_enviado = Column(String, nullable=True)
    tamanho = Column(Integer, nullable=False)
    criado_por_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("User", foreign_keys=[user_id], back_populates="documentos")
    criado_por = relationship("User", foreign_keys=[criado_por_id])
