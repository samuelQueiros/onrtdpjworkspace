from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def agora_utc() -> datetime:
    return datetime.now(UTC)


class FichaAdmissional(Base):
    __tablename__ = "fichas_admissionais"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_fichas_admissionais_user_id"),
        CheckConstraint(
            "status IN ('rascunho','completa')",
            name="ck_fichas_admissionais_status",
        ),
        CheckConstraint(
            "sexo IS NULL OR sexo IN ('feminino','masculino','outro','nao_informado')",
            name="ck_fichas_admissionais_sexo",
        ),
        CheckConstraint(
            "estado_civil IS NULL OR estado_civil IN "
            "('solteiro','casado','divorciado','viuvo','separado','uniao_estavel','outro')",
            name="ck_fichas_admissionais_estado_civil",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    local_nascimento_criptografado = Column(Text, nullable=True)
    uf_nascimento = Column(String(2), nullable=True)
    nacionalidade_criptografada = Column(Text, nullable=True)
    sexo = Column(String(20), nullable=True)
    nome_mae_criptografado = Column(Text, nullable=True)
    nome_pai_criptografado = Column(Text, nullable=True)

    pis_numero_criptografado = Column(Text, nullable=True)
    pis_emissao = Column(Date, nullable=True)
    rg_numero_criptografado = Column(Text, nullable=True)
    rg_emissao = Column(Date, nullable=True)
    rg_orgao_emissor_criptografado = Column(Text, nullable=True)
    ctps_numero_criptografado = Column(Text, nullable=True)
    ctps_serie_criptografada = Column(Text, nullable=True)
    ctps_validade = Column(Date, nullable=True)
    ctps_uf = Column(String(2), nullable=True)
    ctps_emissao = Column(Date, nullable=True)

    telefone_alternativo_criptografado = Column(Text, nullable=True)
    email_alternativo_criptografado = Column(Text, nullable=True)
    endereco_uf = Column(String(2), nullable=True)
    estado_civil = Column(String(30), nullable=True)
    nome_conjuge_criptografado = Column(Text, nullable=True)
    grau_instrucao = Column(String(120), nullable=True)

    salario_criptografado = Column(Text, nullable=True)
    horario_trabalho_criptografado = Column(Text, nullable=True)
    dias_semana_criptografados = Column(Text, nullable=True)
    vale_transporte_criptografado = Column(Text, nullable=True)
    beneficios_criptografados = Column(Text, nullable=True)
    valor_beneficios_criptografado = Column(Text, nullable=True)
    contrato_experiencia_dias = Column(Integer, nullable=True)

    status = Column(String(20), nullable=False, default="rascunho")
    criado_por_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    atualizado_por_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc, onupdate=agora_utc)

    usuario = relationship("User", back_populates="ficha_admissional", foreign_keys=[user_id])
