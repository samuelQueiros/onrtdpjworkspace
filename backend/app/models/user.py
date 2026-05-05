from sqlalchemy import Column, Integer, String, DateTime
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
    criado_em = Column(DateTime, default=datetime.utcnow)

    ferias = relationship("Ferias", back_populates="usuario", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="usuario")
