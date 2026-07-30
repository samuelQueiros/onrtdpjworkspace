from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class HistoricoColaboradorOut(BaseModel):
    campo: Literal["cargo", "departamento", "valor_beneficios"]
    valor_anterior: str | None = None
    valor_novo: str
    tipo_alteracao: Literal["real", "correcao"]
    motivo: str | None = None
    data_vigencia: date
    criado_em: datetime
