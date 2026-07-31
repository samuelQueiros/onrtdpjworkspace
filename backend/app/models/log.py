from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import UTC, datetime
from app.database import Base


def agora_utc() -> datetime:
    return datetime.now(UTC)


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    acao = Column(String, nullable=False)  # ex: "FERIAS_REGISTRADA", "FERIAS_CANCELADA", "USUARIO_CRIADO"
    detalhes = Column(String, nullable=True)
    criado_em = Column(DateTime(timezone=True), default=agora_utc)

    usuario = relationship("User", back_populates="logs")
