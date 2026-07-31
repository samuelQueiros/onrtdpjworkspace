from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.patrimonio import STATUS_EQUIPAMENTO, TIPOS_EQUIPAMENTO

TipoEquipamento = Literal[
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
]
StatusEquipamento = Literal["disponivel", "vinculado", "reservado", "manutencao", "baixado"]


class TextoNormalizadoMixin(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def normalizar_textos(cls, valor):
        if isinstance(valor, str):
            valor = " ".join(valor.split())
            return valor or None
        return valor


class EquipamentoCreate(TextoNormalizadoMixin):
    numero_patrimonio: str | None = Field(default=None, max_length=80)
    numero_serie: str | None = Field(default=None, max_length=120)
    tipo: TipoEquipamento
    marca: str = Field(min_length=1, max_length=100)
    modelo: str = Field(min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=2000)
    estado_conservacao: str = Field(min_length=2, max_length=300)


class EquipamentoUpdate(TextoNormalizadoMixin):
    numero_patrimonio: str | None = Field(default=None, max_length=80)
    numero_serie: str | None = Field(default=None, max_length=120)
    tipo: TipoEquipamento | None = None
    marca: str | None = Field(default=None, min_length=1, max_length=100)
    modelo: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=2000)
    estado_conservacao: str | None = Field(default=None, min_length=2, max_length=300)
    ativo: bool | None = None

    @model_validator(mode="after")
    def impedir_nulos_em_campos_obrigatorios(self):
        for campo in ("tipo", "marca", "modelo", "estado_conservacao", "ativo"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"O campo {campo} não pode ser nulo")
        return self


class VinculoCreate(TextoNormalizadoMixin):
    user_id: int = Field(gt=0)
    observacoes: str | None = Field(default=None, max_length=1000)
    permitir_segunda_maquina: bool = False
    justificativa_excecao: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validar_justificativa(self):
        if self.permitir_segunda_maquina and not self.justificativa_excecao:
            raise ValueError("Informe a justificativa para permitir uma segunda máquina principal")
        return self


class DesvinculoCreate(TextoNormalizadoMixin):
    observacoes: str | None = Field(default=None, max_length=1000)


class ManutencaoCreate(TextoNormalizadoMixin):
    observacoes: str = Field(min_length=3, max_length=2000)
    estado_conservacao: str | None = Field(default=None, max_length=300)


class BaixaCreate(TextoNormalizadoMixin):
    motivo: str = Field(min_length=3, max_length=2000)


class VinculoOut(BaseModel):
    id: int
    equipamento_id: int
    user_id: int
    user_nome: str
    vinculado_em: datetime
    desvinculado_em: datetime | None = None
    vinculado_por_nome: str
    desvinculado_por_nome: str | None = None
    observacoes: str | None = None
    maquina_principal: bool = False
    excecao_maquina_principal: bool = False
    justificativa_excecao: str | None = None


class EventoEquipamentoOut(BaseModel):
    id: int
    tipo: str
    status_anterior: str | None = None
    status_novo: str | None = None
    estado_conservacao: str | None = None
    observacoes: str | None = None
    criado_por_nome: str
    criado_em: datetime


class EquipamentoOut(BaseModel):
    id: int
    numero_patrimonio: str | None = None
    numero_serie: str | None = None
    tipo: str
    marca: str
    modelo: str
    descricao: str | None = None
    estado_conservacao: str
    status: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    vinculo_atual: VinculoOut | None = None
    acoes_permitidas: list[str] = Field(default_factory=list)


class EquipamentoDetalheOut(EquipamentoOut):
    vinculos: list[VinculoOut]
    eventos: list[EventoEquipamentoOut]


class EquipamentosPageOut(BaseModel):
    items: list[EquipamentoOut]
    total: int
    page: int
    page_size: int
    pages: int


class SolicitacaoEquipamentoCreate(TextoNormalizadoMixin):
    tipo_solicitacao: Literal["itens_vinculados", "item_diferente"]
    equipamento_ids: list[int] = Field(min_length=1, max_length=30)
    observacoes: str | None = Field(default=None, max_length=2000)

    @field_validator("equipamento_ids")
    @classmethod
    def ids_unicos(cls, ids: list[int]) -> list[int]:
        if any(item_id <= 0 for item_id in ids):
            raise ValueError("Equipamento inválido")
        if len(ids) != len(set(ids)):
            raise ValueError("Não repita equipamentos na solicitação")
        return ids


class ItemSolicitacaoOut(BaseModel):
    id: int
    equipamento_id: int
    status_item: str
    motivo_remocao: str | None = None
    numero_patrimonio_snapshot: str | None = None
    numero_serie_snapshot: str | None = None
    tipo_snapshot: str
    marca_modelo_snapshot: str
    estado_conservacao_snapshot: str
    observacoes_snapshot: str | None = None
    entregue_em: datetime | None = None
    devolvido_em: datetime | None = None
    estado_conservacao_devolucao: str | None = None
    observacoes_devolucao: str | None = None


class EventoSolicitacaoOut(BaseModel):
    id: int
    tipo: str
    status_anterior: str | None = None
    status_novo: str | None = None
    detalhes: str | None = None
    criado_por_nome: str
    criado_em: datetime


class SolicitacaoEquipamentoOut(BaseModel):
    id: int
    user_id: int
    user_nome: str
    user_cpf_mascarado: str | None = None
    tipo_solicitacao: str
    status: str
    observacoes: str | None = None
    criado_em: datetime
    atualizado_em: datetime
    aprovado_em: datetime | None = None
    aprovado_por_nome: str | None = None
    rejeitado_em: datetime | None = None
    rejeitado_por_nome: str | None = None
    motivo_rejeicao: str | None = None
    cancelado_em: datetime | None = None
    motivo_cancelamento: str | None = None
    entregue_em: datetime | None = None
    entregue_por_nome: str | None = None
    responsavel_entrega_nome: str | None = None
    responsavel_entrega_cargo: str | None = None
    local_entrega: str | None = None
    aceito_em: datetime | None = None
    local_aceite: str | None = None
    termo_versao: str | None = None
    termo_conteudo_hash: str | None = None
    termo_clausulas: str | None = None
    documento_id: int | None = None
    documento_hash: str | None = None
    documento_status: str
    documento_erro: str | None = None
    devolvido_em: datetime | None = None
    estado_conservacao_devolucao: str | None = None
    itens_ausentes_devolucao: str | None = None
    observacoes_devolucao: str | None = None
    itens: list[ItemSolicitacaoOut]
    eventos: list[EventoSolicitacaoOut] = Field(default_factory=list)
    acoes_permitidas: list[str] = Field(default_factory=list)


class SolicitacoesEquipamentosPageOut(BaseModel):
    items: list[SolicitacaoEquipamentoOut]
    total: int
    page: int
    page_size: int
    pages: int


class AprovacaoSolicitacaoCreate(TextoNormalizadoMixin):
    item_ids_aprovados: list[int] = Field(min_length=1)
    motivo_ajuste: str | None = Field(default=None, max_length=2000)
    permitir_segunda_maquina: bool = False
    justificativa_excecao: str | None = Field(default=None, max_length=1000)

    @field_validator("item_ids_aprovados")
    @classmethod
    def itens_unicos(cls, ids: list[int]) -> list[int]:
        if any(item_id <= 0 for item_id in ids):
            raise ValueError("Item de aprovação inválido")
        if len(ids) != len(set(ids)):
            raise ValueError("Não repita itens na aprovação")
        return ids

    @model_validator(mode="after")
    def validar_excecao(self):
        if self.permitir_segunda_maquina and not self.justificativa_excecao:
            raise ValueError("Informe a justificativa para a segunda máquina principal")
        return self


class RejeicaoSolicitacaoCreate(TextoNormalizadoMixin):
    motivo_rejeicao: str = Field(min_length=3, max_length=2000)


class CancelamentoSolicitacaoCreate(TextoNormalizadoMixin):
    motivo: str | None = Field(default=None, max_length=1000)


class ItemEntregaCreate(TextoNormalizadoMixin):
    item_id: int = Field(gt=0)
    estado_conservacao: str = Field(min_length=2, max_length=300)
    observacoes: str | None = Field(default=None, max_length=1000)


class EntregaSolicitacaoCreate(TextoNormalizadoMixin):
    responsavel_entrega_nome: str = Field(min_length=2, max_length=150)
    responsavel_entrega_cargo: str = Field(min_length=2, max_length=120)
    local_entrega: str = Field(min_length=2, max_length=180)
    itens: list[ItemEntregaCreate] = Field(min_length=1)
    permitir_segunda_maquina: bool = False
    justificativa_excecao: str | None = Field(default=None, max_length=1000)

    @field_validator("itens")
    @classmethod
    def itens_unicos(cls, itens: list[ItemEntregaCreate]) -> list[ItemEntregaCreate]:
        ids = [item.item_id for item in itens]
        if len(ids) != len(set(ids)):
            raise ValueError("Não repita itens na entrega")
        return itens

    @model_validator(mode="after")
    def validar_excecao(self):
        if self.permitir_segunda_maquina and not self.justificativa_excecao:
            raise ValueError("Informe a justificativa para a segunda máquina principal")
        return self


class AceiteSolicitacaoCreate(TextoNormalizadoMixin):
    declaracao_aceite: bool
    local_aceite: str = Field(min_length=2, max_length=180)

    @model_validator(mode="after")
    def confirmar_aceite(self):
        if not self.declaracao_aceite:
            raise ValueError("Confirme a leitura e o aceite do termo")
        return self


class ItemDevolucaoCreate(TextoNormalizadoMixin):
    item_id: int = Field(gt=0)
    situacao: Literal["devolvido", "ausente"]
    estado_conservacao: str | None = Field(default=None, max_length=300)
    observacoes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validar_estado_devolvido(self):
        if self.situacao == "devolvido" and not self.estado_conservacao:
            raise ValueError("Informe o estado de conservação do item devolvido")
        return self


class DevolucaoSolicitacaoCreate(TextoNormalizadoMixin):
    itens: list[ItemDevolucaoCreate] = Field(min_length=1)
    estado_conservacao_geral: str = Field(min_length=2, max_length=300)
    observacoes: str | None = Field(default=None, max_length=2000)

    @field_validator("itens")
    @classmethod
    def itens_unicos(cls, itens: list[ItemDevolucaoCreate]) -> list[ItemDevolucaoCreate]:
        ids = [item.item_id for item in itens]
        if len(ids) != len(set(ids)):
            raise ValueError("Não repita itens na devolução")
        return itens


class PendenciasAprovacaoOut(BaseModel):
    ferias: int
    equipamentos: int
    total: int


assert set(TIPOS_EQUIPAMENTO) == set(TipoEquipamento.__args__)
assert set(STATUS_EQUIPAMENTO) == set(StatusEquipamento.__args__)
