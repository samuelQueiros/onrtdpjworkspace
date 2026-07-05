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

    class Config:
        from_attributes = True


class MensagemOut(BaseModel):
    detail: str
