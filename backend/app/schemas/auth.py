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
    dias_usados_total: int = 0
    departamento: Optional[AuthDepartamentoOut] = None
    data_admissao: Optional[str] = None
    data_aniversario: Optional[str] = None
    must_change_password: bool = False


class TokenOut(BaseModel):
    access_token: str
    token_type: str
    user: AuthUserOut


class SessionOut(BaseModel):
    token_type: str
    user: AuthUserOut
