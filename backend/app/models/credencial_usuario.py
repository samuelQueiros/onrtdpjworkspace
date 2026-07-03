from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from app.database import Base


class CredencialUsuario(Base):
    __tablename__ = "credencial_usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    credencial_id = Column(Integer, ForeignKey("credenciais.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
