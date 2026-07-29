from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, model_validator


class FeriasCreate(BaseModel):
    data_inicio: date
    data_fim: date
    ferias_acordo: bool = False

    @model_validator(mode="after")
    def validar_datas(self):
        if self.data_fim < self.data_inicio:
            raise ValueError("data_fim deve ser maior ou igual a data_inicio")
        return self


class FeriasUpdate(BaseModel):
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    ferias_acordo: Optional[bool] = None
    @model_validator(mode="after")
    def validar_datas(self):
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValueError("data_fim deve ser maior ou igual a data_inicio")
        return self


class FeriasAprovar(BaseModel):
    motivo_rejeicao: Optional[str] = None  # preenchido quando rejeitar


class FeriasOut(BaseModel):
    id: int
    user_id: int
    nome_usuario: Optional[str] = None
    cor_usuario: Optional[str] = None
    data_inicio: date
    data_fim: date
    dias_usados: int
    status: str
    ferias_acordo: bool
    motivo_rejeicao: Optional[str]
    criado_em: datetime
    aprovado_por_id: Optional[int] = None
    aprovado_por_nome: Optional[str] = None
    aprovado_em: Optional[datetime] = None
    rejeitado_por_id: Optional[int] = None
    rejeitado_por_nome: Optional[str] = None
    rejeitado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class FeriasVencidaOut(BaseModel):
    ano_referencia: int
    dias: int
    ciclo_inicio: date
    ciclo_fim: date


class SaldoFeriasMovimentoOut(BaseModel):
    tipo: str
    quantidade_dias: int
    data_referencia: date
    motivo: Optional[str] = None
    criado_em: datetime


class MinhasFeriasOut(BaseModel):
    ferias: List[FeriasOut]
    saldo: int
    ciclo_inicio: date
    ciclo_fim: date
    dias_usados_total: int = 0
    dias_direito_total: int = 0
    dias_vencidos: List[FeriasVencidaOut] = []
    movimentos_saldo: List[SaldoFeriasMovimentoOut] = []
    proxima_concessao_ferias: Optional[date] = None


class FeriadoOut(BaseModel):
    data: str
    nome: str


class PeriodoBloqueado(BaseModel):
    data_inicio: date
    data_fim: date


class FeriasMarcadaOut(BaseModel):
    id: int
    user_id: int
    nome: str
    cor: Optional[str] = None
    data_inicio: date
    data_fim: date
    dias_usados: int
    ferias_acordo: bool


class BloqueioManualOut(BaseModel):
    id: int
    data_inicio: date
    data_fim: date
    motivo: str
    tipo: str


class DisponibilidadeOut(BaseModel):
    periodos_bloqueados: List[PeriodoBloqueado]
    ferias_marcadas: List[FeriasMarcadaOut]
    bloqueios_manuais: List[BloqueioManualOut]
