from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from datetime import datetime
from app.database import Base


class CredencialUsuario(Base):
    __tablename__ = "credencial_usuarios"
    __table_args__ = (
        UniqueConstraint("credencial_id", "user_id", name="uq_credencial_usuario"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    credencial_id = Column(Integer, ForeignKey("credenciais.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
