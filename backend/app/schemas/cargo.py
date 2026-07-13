from datetime import datetime

from pydantic import BaseModel, Field


class CargoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)


class CargoUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)


class CargoOut(BaseModel):
    id: int
    nome: str
    total_usuarios: int = 0
    criado_em: datetime

    class Config:
        from_attributes = True
