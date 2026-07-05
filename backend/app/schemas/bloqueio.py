from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class BloqueioCreate(BaseModel):
    data_inicio: date
    data_fim: date
    motivo: str
    tipo: Optional[str] = "bloqueio"


class BloqueioUpdate(BaseModel):
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    motivo: Optional[str] = None
    tipo: Optional[str] = None


class BloqueioOut(BaseModel):
    id: int
    data_inicio: date
    data_fim: date
    motivo: str
    tipo: str
    criado_por_nome: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True


class MensagemOut(BaseModel):
    detail: str
