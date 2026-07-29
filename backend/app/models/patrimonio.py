from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from app.database import Base


TIPOS_EQUIPAMENTO = (
    "notebook",
    "desktop",
    "monitor",
    "mouse",
    "teclado",
    "headset",
    "dock_station",
    "carregador",
    "cabo_energia",
    "adaptador",
    "outro",
)
STATUS_EQUIPAMENTO = ("disponivel", "vinculado", "reservado", "manutencao", "baixado")
STATUS_SOLICITACAO = (
    "pendente",
    "rejeitada",
    "cancelada",
    "aguardando_entrega",
    "aguardando_aceite",
    "aceite_registrado_aguardando_documento",
    "entregue",
    "devolvida",
)


def agora_utc() -> datetime:
    return datetime.now(UTC)


class Equipamento(Base):
    __tablename__ = "equipamentos"
    __table_args__ = (
        UniqueConstraint("numero_patrimonio", name="uq_equipamentos_numero_patrimonio"),
        UniqueConstraint("numero_serie", name="uq_equipamentos_numero_serie"),
        CheckConstraint(
            "tipo IN ('notebook','desktop','monitor','mouse','teclado','headset','dock_station',"
            "'carregador','cabo_energia','adaptador','outro')",
            name="ck_equipamentos_tipo",
        ),
        CheckConstraint(
            "status IN ('disponivel','vinculado','reservado','manutencao','baixado')",
            name="ck_equipamentos_status",
        ),
        Index("ix_equipamentos_busca", "tipo", "status", "ativo"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_patrimonio = Column(String(80), nullable=True)
    numero_serie = Column(String(120), nullable=True)
    tipo = Column(String(40), nullable=False)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(120), nullable=False)
    descricao = Column(Text, nullable=True)
    estado_conservacao = Column(String(300), nullable=False)
    status = Column(String(30), nullable=False, default="disponivel")
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc, onupdate=agora_utc)

    vinculos = relationship("EquipamentoVinculo", back_populates="equipamento")
    eventos = relationship("EquipamentoEvento", back_populates="equipamento")
    itens_solicitacao = relationship("SolicitacaoEquipamentoItem", back_populates="equipamento")


class EquipamentoVinculo(Base):
    __tablename__ = "equipamento_vinculos"
    __table_args__ = (
        Index(
            "uq_equipamento_vinculo_ativo",
            "equipamento_id",
            unique=True,
            postgresql_where=text("desvinculado_em IS NULL"),
        ),
        Index(
            "uq_usuario_maquina_principal_padrao_ativa",
            "user_id",
            unique=True,
            postgresql_where=text(
                "desvinculado_em IS NULL AND maquina_principal IS TRUE "
                "AND excecao_maquina_principal IS FALSE"
            ),
        ),
        Index("ix_equipamento_vinculos_user_ativo", "user_id", "desvinculado_em"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id", ondelete="RESTRICT"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    vinculado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
    desvinculado_em = Column(DateTime(timezone=True), nullable=True)
    vinculado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    desvinculado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    observacoes = Column(Text, nullable=True)
    maquina_principal = Column(Boolean, nullable=False, default=False)
    excecao_maquina_principal = Column(Boolean, nullable=False, default=False)
    justificativa_excecao = Column(Text, nullable=True)

    equipamento = relationship("Equipamento", back_populates="vinculos")
    usuario = relationship("User", foreign_keys=[user_id])
    vinculado_por = relationship("User", foreign_keys=[vinculado_por_id])
    desvinculado_por = relationship("User", foreign_keys=[desvinculado_por_id])


class EquipamentoEvento(Base):
    __tablename__ = "equipamento_eventos"
    __table_args__ = (Index("ix_equipamento_eventos_equipamento_data", "equipamento_id", "criado_em"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id", ondelete="RESTRICT"), nullable=False)
    tipo = Column(String(50), nullable=False)
    status_anterior = Column(String(30), nullable=True)
    status_novo = Column(String(30), nullable=True)
    estado_conservacao = Column(String(300), nullable=True)
    observacoes = Column(Text, nullable=True)
    criado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)

    equipamento = relationship("Equipamento", back_populates="eventos")
    criado_por = relationship("User", foreign_keys=[criado_por_id])


class TermoEquipamentoVersao(Base):
    __tablename__ = "termo_equipamento_versoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(30), nullable=False, unique=True)
    vigente_desde = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
    conteudo_hash = Column(String(64), nullable=False)
    clausulas = Column(Text, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)


class SolicitacaoEquipamento(Base):
    __tablename__ = "solicitacoes_equipamentos"
    __table_args__ = (
        CheckConstraint(
            "tipo_solicitacao IN ('itens_vinculados','item_diferente')",
            name="ck_solicitacoes_equipamentos_tipo",
        ),
        CheckConstraint(
            "status IN ('pendente','rejeitada','cancelada','aguardando_entrega',"
            "'aguardando_aceite','aceite_registrado_aguardando_documento','entregue','devolvida')",
            name="ck_solicitacoes_equipamentos_status",
        ),
        CheckConstraint(
            "documento_status IN ('pendente','gerando','gerado','falha')",
            name="ck_solicitacoes_equipamentos_documento_status",
        ),
        Index("ix_solicitacoes_equipamentos_user_status", "user_id", "status"),
        Index("ix_solicitacoes_equipamentos_status_criado", "status", "criado_em"),
        UniqueConstraint("documento_id", name="uq_solicitacoes_equipamentos_documento"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    tipo_solicitacao = Column(String(30), nullable=False)
    status = Column(String(60), nullable=False, default="pendente")
    observacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc, onupdate=agora_utc)
    nome_colaborador_snapshot = Column(String(150), nullable=False)
    cpf_snapshot_criptografado = Column(Text, nullable=False)
    cargo_snapshot = Column(String(120), nullable=False)
    departamento_snapshot = Column(String(150), nullable=False)

    aprovado_em = Column(DateTime(timezone=True), nullable=True)
    aprovado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    rejeitado_em = Column(DateTime(timezone=True), nullable=True)
    rejeitado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    motivo_rejeicao = Column(Text, nullable=True)
    cancelado_em = Column(DateTime(timezone=True), nullable=True)
    cancelado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    motivo_cancelamento = Column(Text, nullable=True)

    entregue_em = Column(DateTime(timezone=True), nullable=True)
    entregue_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    responsavel_entrega_nome = Column(String(150), nullable=True)
    responsavel_entrega_cargo = Column(String(120), nullable=True)
    local_entrega = Column(String(180), nullable=True)

    aceito_em = Column(DateTime(timezone=True), nullable=True)
    aceite_ip = Column(String(64), nullable=True)
    aceite_request_id = Column(String(80), nullable=True)
    local_aceite = Column(String(180), nullable=True)
    aceite_declaracao = Column(Boolean, nullable=False, default=False)
    termo_versao_id = Column(Integer, ForeignKey("termo_equipamento_versoes.id", ondelete="RESTRICT"), nullable=True)
    termo_html_snapshot_criptografado = Column(Text, nullable=True)
    documento_id = Column(Integer, ForeignKey("documentos.id", ondelete="SET NULL"), nullable=True)
    documento_hash = Column(String(64), nullable=True)
    documento_status = Column(String(30), nullable=False, default="pendente")
    documento_erro = Column(Text, nullable=True)

    devolvido_em = Column(DateTime(timezone=True), nullable=True)
    devolvido_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    recebido_devolucao_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    estado_conservacao_devolucao = Column(String(300), nullable=True)
    itens_ausentes_devolucao = Column(Text, nullable=True)
    observacoes_devolucao = Column(Text, nullable=True)

    usuario = relationship("User", foreign_keys=[user_id])
    aprovado_por = relationship("User", foreign_keys=[aprovado_por_id])
    rejeitado_por = relationship("User", foreign_keys=[rejeitado_por_id])
    entregue_por = relationship("User", foreign_keys=[entregue_por_id])
    termo_versao = relationship("TermoEquipamentoVersao")
    documento = relationship("Documento", foreign_keys=[documento_id])
    itens = relationship(
        "SolicitacaoEquipamentoItem",
        back_populates="solicitacao",
        cascade="all, delete-orphan",
        order_by="SolicitacaoEquipamentoItem.id",
    )
    eventos = relationship(
        "SolicitacaoEquipamentoEvento",
        back_populates="solicitacao",
        cascade="all, delete-orphan",
        order_by="SolicitacaoEquipamentoEvento.criado_em",
    )


class SolicitacaoEquipamentoItem(Base):
    __tablename__ = "solicitacao_equipamento_itens"
    __table_args__ = (
        UniqueConstraint("solicitacao_id", "equipamento_id", name="uq_solicitacao_equipamento_item"),
        CheckConstraint(
            "status_item IN ('solicitado','aprovado','removido','entregue','devolvido','ausente')",
            name="ck_solicitacao_equipamento_itens_status",
        ),
        CheckConstraint(
            "reserva_liberada_em IS NULL OR reservado_em IS NOT NULL",
            name="ck_solicitacao_equipamento_itens_reserva",
        ),
        Index("ix_solicitacao_equipamento_itens_equipamento", "equipamento_id"),
        Index(
            "uq_solicitacao_item_reserva_ativa",
            "equipamento_id",
            unique=True,
            postgresql_where=text("reservado_em IS NOT NULL AND reserva_liberada_em IS NULL"),
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    solicitacao_id = Column(
        Integer,
        ForeignKey("solicitacoes_equipamentos.id", ondelete="CASCADE"),
        nullable=False,
    )
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id", ondelete="RESTRICT"), nullable=False)
    status_item = Column(String(30), nullable=False, default="solicitado")
    motivo_remocao = Column(Text, nullable=True)
    removido_em = Column(DateTime(timezone=True), nullable=True)
    removido_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    reservado_em = Column(DateTime(timezone=True), nullable=True)
    reserva_liberada_em = Column(DateTime(timezone=True), nullable=True)
    vinculo_criado_entrega_id = Column(
        Integer,
        ForeignKey("equipamento_vinculos.id", ondelete="SET NULL"),
        nullable=True,
    )
    numero_patrimonio_snapshot = Column(String(80), nullable=True)
    numero_serie_snapshot = Column(String(120), nullable=True)
    tipo_snapshot = Column(String(40), nullable=False)
    marca_modelo_snapshot = Column(String(240), nullable=False)
    estado_conservacao_snapshot = Column(String(300), nullable=False)
    observacoes_snapshot = Column(Text, nullable=True)
    entregue_em = Column(DateTime(timezone=True), nullable=True)
    devolvido_em = Column(DateTime(timezone=True), nullable=True)
    estado_conservacao_devolucao = Column(String(300), nullable=True)
    observacoes_devolucao = Column(Text, nullable=True)

    solicitacao = relationship("SolicitacaoEquipamento", back_populates="itens")
    equipamento = relationship("Equipamento", back_populates="itens_solicitacao")
    vinculo_criado_entrega = relationship("EquipamentoVinculo", foreign_keys=[vinculo_criado_entrega_id])
    removido_por = relationship("User", foreign_keys=[removido_por_id])


class SolicitacaoEquipamentoEvento(Base):
    __tablename__ = "solicitacao_equipamento_eventos"
    __table_args__ = (Index("ix_solicitacao_equipamento_eventos_data", "solicitacao_id", "criado_em"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    solicitacao_id = Column(
        Integer,
        ForeignKey("solicitacoes_equipamentos.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo = Column(String(60), nullable=False)
    status_anterior = Column(String(60), nullable=True)
    status_novo = Column(String(60), nullable=True)
    detalhes = Column(Text, nullable=True)
    criado_por_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)

    solicitacao = relationship("SolicitacaoEquipamento", back_populates="eventos")
    criado_por = relationship("User", foreign_keys=[criado_por_id])
