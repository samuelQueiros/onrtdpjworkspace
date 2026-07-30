from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class HistoricoSalarialOut(BaseModel):
    data_vigencia: date
    salario: Decimal
    tipo: Literal["reajuste", "correcao"]
    motivo: str | None = None
    criado_em: datetime
