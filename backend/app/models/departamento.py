from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Departamento(Base):
    __tablename__ = "departamentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    limite_simultaneo = Column(Integer, default=2)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuarios = relationship("User", back_populates="departamento")
