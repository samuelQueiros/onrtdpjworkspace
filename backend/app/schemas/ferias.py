from pydantic import BaseModel, model_validator
from typing import Optional, List
from datetime import date, datetime


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
    status: Optional[str] = None          # apenas admin: "aprovada" | "rejeitada"
    motivo_rejeicao: Optional[str] = None  # apenas admin

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
    data_inicio: date
    data_fim: date
    dias_usados: int
    status: str
    ferias_acordo: bool
    motivo_rejeicao: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True


class PeriodoBloqueado(BaseModel):
    data_inicio: date
    data_fim: date


class DisponibilidadeOut(BaseModel):
    periodos_bloqueados: List[PeriodoBloqueado]
