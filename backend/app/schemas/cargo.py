from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CargoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)

    @field_validator("nome", mode="before")
    @classmethod
    def normalizar_nome(cls, valor):
        return " ".join(str(valor or "").split())


class CargoUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)

    @field_validator("nome", mode="before")
    @classmethod
    def normalizar_nome(cls, valor):
        return " ".join(str(valor or "").split())


class CargoOut(BaseModel):
    id: int
    nome: str
    total_usuarios: int = 0
    criado_em: datetime

    class Config:
        from_attributes = True
