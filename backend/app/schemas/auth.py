from pydantic import BaseModel
from typing import Optional


class AuthDepartamentoOut(BaseModel):
    id: int
    nome: str


class AuthUserOut(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    dias_totais: int
    dias_restantes: int
    departamento: Optional[AuthDepartamentoOut] = None
    data_admissao: Optional[str] = None
    data_aniversario: Optional[str] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str
    user: AuthUserOut
