from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


def agora_utc() -> datetime:
    return datetime.now(UTC)


class Envio(Base):
    """Rastreamento de um e-mail de lembrete de ferias enviado a partir de um Alerta."""

    __tablename__ = "envios"
    __table_args__ = (
        CheckConstraint(
            "status IN ('enviado','monitorando','erro_definitivo','respondido','sem_retorno')",
            name="ck_envios_status",
        ),
        UniqueConstraint("alerta_id", name="uq_envios_alerta_id"),
        UniqueConstraint("message_id", name="uq_envios_message_id"),
        UniqueConstraint("token_rastreio", name="uq_envios_token_rastreio"),
        Index("ix_envios_status", "status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    # RESTRICT: nao permite excluir fisicamente um Alerta/Ferias que ja tem e-mail enviado.
    alerta_id = Column(Integer, ForeignKey("alertas.id", ondelete="RESTRICT"), nullable=False)

    # Snapshots do momento do envio - o historico nao deve mudar retroativamente se o
    # alerta/ferias ou a configuracao de destinatario forem alterados depois.
    colaborador_nome_snapshot = Column(String(150), nullable=False)
    periodo_ferias_snapshot = Column(String(60), nullable=False)
    destinatario_email_snapshot = Column(String(255), nullable=False)

    message_id = Column(String(255), nullable=False)
    token_rastreio = Column(String(64), nullable=False)
    status = Column(String(30), nullable=False, default="enviado")
    erro_codigo = Column(String(10), nullable=True)
    erro_mensagem = Column(Text, nullable=True)
    tentativas_verificacao = Column(Integer, nullable=False, default=0)

    enviado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
    prazo_limite = Column(DateTime(timezone=True), nullable=False)
    ultima_verificacao_em = Column(DateTime(timezone=True), nullable=True)
    lido_em = Column(DateTime(timezone=True), nullable=True)
    respondido_em = Column(DateTime(timezone=True), nullable=True)
    resposta_texto = Column(Text, nullable=True)
    resposta_bruta = Column(Text, nullable=True)

    enviado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc, onupdate=agora_utc)

    alerta = relationship("Alerta")
    enviado_por = relationship("User", foreign_keys=[enviado_por_id])
    eventos = relationship(
        "EnvioEvento",
        back_populates="envio",
        cascade="all, delete-orphan",
        order_by="EnvioEvento.criado_em",
    )


class EnvioEvento(Base):
    """Trilha de auditoria por transicao de estado de um Envio (mesmo padrao de
    equipamento_eventos/solicitacao_equipamento_eventos)."""

    __tablename__ = "envio_eventos"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('envio_criado','verificacao_realizada','bounce_temporario',"
            "'bounce_definitivo','resposta_detectada','prazo_estourado','erro_verificacao')",
            name="ck_envio_eventos_tipo",
        ),
        Index("ix_envio_eventos_envio_data", "envio_id", "criado_em"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    envio_id = Column(Integer, ForeignKey("envios.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(50), nullable=False)
    status_anterior = Column(String(30), nullable=True)
    status_novo = Column(String(30), nullable=True)
    detalhes = Column(Text, nullable=True)
    # nullable=True: ao contrario de equipamento_eventos/solicitacao_equipamento_eventos,
    # transicoes disparadas pelo job de monitoramento (bounce, resposta, prazo estourado)
    # nao tem current_user - so eventos criados pela acao humana de enviar tem criado_por_id.
    criado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)

    envio = relationship("Envio", back_populates="eventos")
    criado_por = relationship("User", foreign_keys=[criado_por_id])
