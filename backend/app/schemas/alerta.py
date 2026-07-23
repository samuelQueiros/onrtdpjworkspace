from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class AlertaOut(BaseModel):
    id: int
    ferias_id: Optional[int]
    tipo: str
    mensagem: str
    lido: bool
    criado_em: datetime
    ferias_data_inicio: Optional[date]
    ferias_data_fim: Optional[date]
    ferias_usuario: Optional[str]
    ferias_dias_usados: Optional[int] = None
    cargo_usuario: Optional[str] = None
    ciclo_inicio: Optional[date] = None
    ciclo_fim: Optional[date] = None
    retorno_trabalho: Optional[date] = None

    class Config:
        from_attributes = True
