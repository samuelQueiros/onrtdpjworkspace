from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String

from app.database import Base


def agora_utc() -> datetime:
    return datetime.now(UTC)


class Configuracao(Base):
    """Linha unica (id=1) de configuracao global do sistema."""

    __tablename__ = "configuracao"
    __table_args__ = (CheckConstraint("id = 1", name="ck_configuracao_singleton"),)

    id = Column(Integer, primary_key=True, default=1)
    email_destinatario = Column(String(255), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc, onupdate=agora_utc)
