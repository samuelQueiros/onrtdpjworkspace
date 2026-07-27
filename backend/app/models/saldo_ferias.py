from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.database import Base


class SaldoFeriasMovimento(Base):
    __tablename__ = "saldo_ferias_movimentos"
    __table_args__ = (
        UniqueConstraint("chave_idempotencia", name="uq_saldo_ferias_movimento_chave"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String, nullable=False)
    quantidade_dias = Column(Integer, nullable=False)
    data_referencia = Column(Date, nullable=False)
    motivo = Column(String, nullable=True)
    criado_por_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    chave_idempotencia = Column(String, nullable=False)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
