from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CredencialCreate(BaseModel):
    descricao: str
    email: str
    senha: str


class CredencialUpdate(BaseModel):
    descricao: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None


class CredencialOut(BaseModel):
    id: int
    descricao: str
    email: str
    criado_em: datetime
    atualizado_em: datetime
    total_usuarios: int

    class Config:
        from_attributes = True


class CredencialComSenhaOut(CredencialOut):
    senha: str


class PermissoesUpdate(BaseModel):
    user_ids: List[int]
