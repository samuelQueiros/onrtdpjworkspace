from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # "user" ou "admin"
    dias_totais = Column(Integer, default=30)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=True)
    data_admissao = Column(Date, nullable=True)
    data_aniversario = Column(Date, nullable=True)
    cor = Column(String, nullable=True)  # cor HEX para identificação visual
    criado_em = Column(DateTime, default=datetime.utcnow)

    ferias = relationship("Ferias", back_populates="usuario", foreign_keys="[Ferias.user_id]", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="usuario")
    departamento = relationship("Departamento", back_populates="usuarios")
    documentos = relationship(
        "Documento",
        back_populates="usuario",
        foreign_keys="Documento.user_id",
        cascade="all, delete-orphan",
    )
