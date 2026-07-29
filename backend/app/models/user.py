from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, ForeignKey, UniqueConstraint, true
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("cpf_hash", name="uq_users_cpf_hash"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # "user" ou "admin"
    dias_totais = Column(Integer, default=30)
    saldo_manual_dias = Column(Integer, nullable=True, default=None)  # override manual do saldo acumulado (None = automatico)
    proxima_concessao_ferias = Column(Date, nullable=True)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=True)
    data_admissao = Column(Date, nullable=True)
    data_aniversario = Column(Date, nullable=True)
    cor = Column(String, nullable=True)  # cor HEX para identificação visual
    telefone = Column(String, nullable=True)
    telefone_emergencia = Column(String, nullable=True)
    telefone_emergencia_2 = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    dados_bancarios = Column(String, nullable=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
    must_change_password = Column(Boolean, nullable=False, default=True, server_default=true())
    token_version = Column(Integer, nullable=False, default=0)
    cpf_criptografado = Column(String, nullable=True)
    cpf_hash = Column(String(64), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    ferias = relationship("Ferias", back_populates="usuario", foreign_keys="[Ferias.user_id]", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="usuario")
    departamento = relationship("Departamento", back_populates="usuarios")
    cargo = relationship("Cargo", back_populates="usuarios")
    documentos = relationship(
        "Documento",
        back_populates="usuario",
        foreign_keys="Documento.user_id",
        cascade="all, delete-orphan",
    )
    credenciais = relationship(
        "Credencial",
        secondary="credencial_usuarios",
        back_populates="usuarios",
    )
