from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class RelatorioDepartamentoOut(BaseModel):
    id: int
    nome: str


class RelatorioFeriasPeriodoOut(BaseModel):
    id: int
    data_inicio: date
    data_fim: date
    dias_usados: int


class RelatorioFeriasOut(RelatorioFeriasPeriodoOut):
    status: str
    ferias_acordo: bool


class RelatorioColaboradorOut(BaseModel):
    id: int
    nome: str
    email: str
    departamento: Optional[RelatorioDepartamentoOut]
    dias_totais: int
    dias_usados: int
    dias_restantes: int
    ciclo_inicio: date
    ciclo_fim: date
    ferias: list[RelatorioFeriasOut]
    ferias_acordo: list[RelatorioFeriasPeriodoOut]
    ferias_pendentes: list[RelatorioFeriasPeriodoOut]


class RelatorioColaboradoresOut(BaseModel):
    colaboradores: list[RelatorioColaboradorOut]


class PessoaEmFeriasOut(BaseModel):
    id: int
    nome: str
    cor: Optional[str]
    data_inicio: date
    data_fim: date
    dias_restantes: int


class ProximaFeriasOut(BaseModel):
    id: int
    nome_usuario: str
    cor: Optional[str]
    data_inicio: date
    data_fim: date
    dias_usados: int


class AlertaContabilidadeOut(BaseModel):
    ferias_id: int
    nome_usuario: str
    data_inicio: date
    data_fim: date
    dias_para_inicio: int


class DashboardOut(BaseModel):
    total_colaboradores: int
    total_ferias_aprovadas: int
    total_ferias_pendentes: int
    total_ferias_rejeitadas: int
    total_departamentos: int
    pessoas_em_ferias: list[PessoaEmFeriasOut]
    proximas_ferias: list[ProximaFeriasOut]
    alertas_contabilidade: list[AlertaContabilidadeOut]


class LogDetalhadoOut(BaseModel):
    id: int
    user_id: Optional[int]
    nome_usuario: str
    email_usuario: Optional[str]
    acao: str
    detalhes: Optional[str]
    criado_em: datetime


class LogsPageOut(BaseModel):
    items: list[LogDetalhadoOut]
    page: int
    page_size: int
    total: int
