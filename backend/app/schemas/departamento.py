from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class DepartamentoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    limite_simultaneo: int = Field(default=2, ge=1, le=50)

    @field_validator("nome", mode="before")
    @classmethod
    def normalizar_nome(cls, valor):
        return " ".join(str(valor or "").split())


class DepartamentoUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    limite_simultaneo: Optional[int] = Field(default=None, ge=1, le=50)

    @field_validator("nome", mode="before")
    @classmethod
    def normalizar_nome(cls, valor):
        return None if valor is None else " ".join(str(valor).split())


class DepartamentoOut(BaseModel):
    id: int
    nome: str
    limite_simultaneo: int
    criado_em: datetime

    class Config:
        from_attributes = True


class DepartamentoComTotalOut(DepartamentoOut):
    total_usuarios: int
