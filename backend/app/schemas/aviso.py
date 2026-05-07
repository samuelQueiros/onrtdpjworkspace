from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AvisoCreate(BaseModel):
    titulo: str
    conteudo: str
    fixado: bool = False
    data_expiracao: Optional[date] = None


class AvisoUpdate(BaseModel):
    titulo: Optional[str] = None
    conteudo: Optional[str] = None
    fixado: Optional[bool] = None
    data_expiracao: Optional[date] = None


class AvisoOut(BaseModel):
    id: int
    titulo: str
    conteudo: str
    fixado: bool
    data_expiracao: Optional[date]
    criado_por_nome: str
    criado_em: datetime

    class Config:
        from_attributes = True
