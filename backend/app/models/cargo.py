from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    usuarios = relationship("User", back_populates="cargo")
