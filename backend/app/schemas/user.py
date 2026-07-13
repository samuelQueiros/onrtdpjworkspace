from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal, Optional
from datetime import datetime, date


class DadosBancarios(BaseModel):
    banco: Optional[str] = Field(default=None, max_length=100)
    agencia: Optional[str] = Field(default=None, max_length=30)
    conta: Optional[str] = Field(default=None, max_length=30)
    cpf_titular: Optional[str] = Field(default=None, max_length=14)
    nome_titular: Optional[str] = Field(default=None, max_length=150)
    chave_pix: Optional[str] = Field(default=None, max_length=150)

    @field_validator("banco", "agencia", "conta", "cpf_titular", "nome_titular", "chave_pix", mode="before")
    @classmethod
    def normalizar_campos(cls, valor):
        if valor is None:
            return None
        texto = " ".join(str(valor).split())
        return texto or None


class Endereco(BaseModel):
    logradouro: Optional[str] = Field(default=None, max_length=200)
    numero: Optional[str] = Field(default=None, max_length=20)
    bairro: Optional[str] = Field(default=None, max_length=100)
    cidade: Optional[str] = Field(default=None, max_length=100)
    cep: Optional[str] = Field(default=None, max_length=9)

    @field_validator("logradouro", "numero", "bairro", "cidade", "cep", mode="before")
    @classmethod
    def normalizar_campos(cls, valor):
        if valor is None:
            return None
        texto = " ".join(str(valor).split())
        return texto or None


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
    endereco: Optional[Endereco] = None
    dados_bancarios: Optional[DadosBancarios] = None
    cargo: Optional[str] = Field(default=None, max_length=100)

    @field_validator("nome", "telefone", "telefone_emergencia", "cargo", mode="before")
    @classmethod
    def normalizar_textos(cls, valor):
        if valor is None:
            return None
        texto = " ".join(str(valor).split())
        return texto or None


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
    endereco: Optional[Endereco] = None
    dados_bancarios: Optional[DadosBancarios] = None
    cargo: Optional[str] = Field(default=None, max_length=100)

    @field_validator("nome", "telefone", "telefone_emergencia", "cargo", mode="before")
    @classmethod
    def normalizar_textos(cls, valor):
        if valor is None:
            return None
        texto = " ".join(str(valor).split())
        return texto or None


class UserConfigUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha_atual: Optional[str] = None
    nova_senha: Optional[str] = Field(default=None, min_length=8, max_length=128)


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
    endereco: Optional[Endereco] = None
    dados_bancarios: Optional[DadosBancarios] = None


class AniversarianteOut(BaseModel):
    nome: str
    data_aniversario: date
