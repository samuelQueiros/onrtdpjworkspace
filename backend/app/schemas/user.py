from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from datetime import datetime, date


class UserCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    role: Literal["user", "admin"] = "user"
    dias_totais: int = Field(default=30, ge=0, le=365)
    departamento_id: Optional[int] = None
    data_admissao: Optional[date] = None
    data_aniversario: Optional[date] = None
    cor: Optional[str] = None
    telefone: Optional[str] = Field(default=None, max_length=30)
    telefone_emergencia: Optional[str] = Field(default=None, max_length=30)
    endereco: Optional[str] = Field(default=None, max_length=500)
    dados_bancarios: Optional[str] = Field(default=None, max_length=500)
    cargo: Optional[str] = Field(default=None, max_length=100)


class UserUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    dias_totais: Optional[int] = Field(default=None, ge=0, le=365)
    departamento_id: Optional[int] = None
    data_admissao: Optional[date] = None
    data_aniversario: Optional[date] = None
    senha: Optional[str] = Field(default=None, min_length=8, max_length=128)
    cor: Optional[str] = None
    telefone: Optional[str] = Field(default=None, max_length=30)
    telefone_emergencia: Optional[str] = Field(default=None, max_length=30)
    endereco: Optional[str] = Field(default=None, max_length=500)
    dados_bancarios: Optional[str] = Field(default=None, max_length=500)
    cargo: Optional[str] = Field(default=None, max_length=100)
    ativo: Optional[bool] = None


class UserConfigUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha_atual: Optional[str] = None
    nova_senha: Optional[str] = None


class UserOut(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    dias_totais: int
    criado_em: datetime

    class Config:
        from_attributes = True


class UserWithDias(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    dias_totais: int
    dias_restantes: int

    class Config:
        from_attributes = True


class UserDepartamentoOut(BaseModel):
    id: int
    nome: str


class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    dias_totais: int
    dias_restantes: int
    departamento_id: Optional[int] = None
    departamento: Optional[UserDepartamentoOut] = None
    data_admissao: Optional[date] = None
    data_aniversario: Optional[date] = None
    cor: Optional[str] = None
    telefone: Optional[str] = None
    cargo: Optional[str] = None
    ativo: bool = True
    criado_em: datetime


class UserSensitiveResponse(BaseModel):
    telefone_emergencia: Optional[str] = None
    endereco: Optional[str] = None
    dados_bancarios: Optional[str] = None


class AniversarianteOut(BaseModel):
    nome: str
    data_aniversario: date
