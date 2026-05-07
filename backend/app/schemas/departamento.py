from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DepartamentoCreate(BaseModel):
    nome: str
    limite_simultaneo: int = 2


class DepartamentoUpdate(BaseModel):
    nome: Optional[str] = None
    limite_simultaneo: Optional[int] = None


class DepartamentoOut(BaseModel):
    id: int
    nome: str
    limite_simultaneo: int
    criado_em: datetime

    class Config:
        from_attributes = True
