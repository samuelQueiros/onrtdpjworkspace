from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Literal, Optional
from datetime import datetime, date
import re

from app.core.cpf import formatar_cpf, validar_cpf


def _validar_telefone(valor: str | None) -> str | None:
    if valor is None:
        return None
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) not in {10, 11}:
        raise ValueError("Telefone deve conter DDD e 10 ou 11 digitos")
    return valor


def _validar_campos_completos(valores: dict, rotulo: str) -> None:
    preenchidos = [bool(valor) for valor in valores.values()]
    if any(preenchidos) and not all(preenchidos):
        raise ValueError(f"Todos os campos de {rotulo} devem ser preenchidos")


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

    @field_validator("cpf_titular")
    @classmethod
    def validar_cpf_do_titular(cls, valor: str | None) -> str | None:
        return formatar_cpf(validar_cpf(valor)) if valor else None


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

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, valor: str | None) -> str | None:
        if valor and len(re.sub(r"\D", "", valor)) != 8:
            raise ValueError("CEP deve conter 8 digitos")
        return valor


class UserCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    role: Literal["user", "admin"]
    dias_totais: int = Field(ge=0, le=365)
    saldo_inicial_dias: int = Field(ge=0, le=3650)
    proxima_concessao_ferias: Optional[date] = None
    departamento_id: int = Field(gt=0)
    data_admissao: date
    data_aniversario: date
    cor: str = Field(min_length=4, max_length=20)
    telefone: str = Field(min_length=1, max_length=30)
    telefone_emergencia: str = Field(min_length=1, max_length=30)
    telefone_emergencia_2: str = Field(min_length=1, max_length=30)
    endereco: Endereco
    dados_bancarios: DadosBancarios
    cargo: str = Field(min_length=1, max_length=100)
    cpf: str = Field(min_length=11, max_length=14)

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor):
        return str(valor).strip().lower() if valor is not None else valor

    @field_validator("nome", "telefone", "telefone_emergencia", "telefone_emergencia_2", "cargo", "cor", mode="before")
    @classmethod
    def normalizar_textos(cls, valor):
        if valor is None:
            return None
        texto = " ".join(str(valor).split())
        return texto or None

    @field_validator("telefone", "telefone_emergencia", "telefone_emergencia_2")
    @classmethod
    def validar_telefones(cls, valor):
        return _validar_telefone(valor)

    @field_validator("cpf")
    @classmethod
    def validar_cpf_colaborador(cls, valor: str) -> str:
        return formatar_cpf(validar_cpf(valor))

    @model_validator(mode="after")
    def validar_campos_estruturados(self):
        endereco = self.endereco.model_dump()
        bancarios = self.dados_bancarios.model_dump()
        if any(not valor for valor in endereco.values()):
            raise ValueError("Todos os campos de endereco devem ser preenchidos")
        if any(not valor for valor in bancarios.values()):
            raise ValueError("Todos os campos de dados bancarios devem ser preenchidos")
        return self


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
    telefone_emergencia_2: Optional[str] = Field(default=None, max_length=30)
    endereco: Optional[Endereco] = None
    dados_bancarios: Optional[DadosBancarios] = None
    cargo: Optional[str] = Field(default=None, max_length=100)
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=14)
    saldo_atual_dias: Optional[int] = Field(default=None, ge=0, le=3650)
    motivo_ajuste_saldo: Optional[str] = Field(default=None, min_length=3, max_length=500)
    proxima_concessao_ferias: Optional[date] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor):
        return str(valor).strip().lower() if valor is not None else valor

    @field_validator("nome", "telefone", "telefone_emergencia", "telefone_emergencia_2", "cargo", mode="before")
    @classmethod
    def normalizar_textos(cls, valor):
        if valor is None:
            return None
        texto = " ".join(str(valor).split())
        return texto or None

    @field_validator("telefone", "telefone_emergencia", "telefone_emergencia_2")
    @classmethod
    def validar_telefones(cls, valor):
        return _validar_telefone(valor)

    @field_validator("cpf")
    @classmethod
    def validar_cpf_colaborador(cls, valor: str | None) -> str | None:
        return formatar_cpf(validar_cpf(valor)) if valor else None

    @model_validator(mode="after")
    def validar_campos_estruturados(self):
        if self.endereco is not None:
            _validar_campos_completos(self.endereco.model_dump(), "endereco")
        if self.dados_bancarios is not None:
            _validar_campos_completos(self.dados_bancarios.model_dump(), "dados bancarios")
        return self


class UserConfigUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha_atual: Optional[str] = None
    nova_senha: Optional[str] = Field(default=None, min_length=8, max_length=128)
    telefone: Optional[str] = Field(default=None, max_length=30)
    telefone_emergencia: Optional[str] = Field(default=None, max_length=30)
    telefone_emergencia_2: Optional[str] = Field(default=None, max_length=30)

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor):
        return str(valor).strip().lower() if valor is not None else valor

    @field_validator("telefone", "telefone_emergencia", "telefone_emergencia_2", mode="before")
    @classmethod
    def normalizar_telefones(cls, valor):
        if valor is None:
            return None
        texto = " ".join(str(valor).split())
        return _validar_telefone(texto or None)


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
    dias_usados_total: int = 0
    departamento_id: Optional[int] = None
    departamento: Optional[UserDepartamentoOut] = None
    data_admissao: Optional[date] = None
    data_aniversario: Optional[date] = None
    cor: Optional[str] = None
    telefone: Optional[str] = None
    cpf_mascarado: Optional[str] = None
    cargo: Optional[str] = None
    ativo: bool = True
    must_change_password: bool = False
    saldo_manual_dias: Optional[int] = None
    proxima_concessao_ferias: Optional[date] = None
    criado_em: datetime


class UserSensitiveResponse(BaseModel):
    cpf: Optional[str] = None
    telefone_emergencia: Optional[str] = None
    telefone_emergencia_2: Optional[str] = None
    endereco: Optional[Endereco] = None
    dados_bancarios: Optional[DadosBancarios] = None


class MeuPerfilOut(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    cor: Optional[str] = None
    cargo: Optional[str] = None
    departamento: Optional[UserDepartamentoOut] = None
    data_admissao: Optional[date] = None
    data_aniversario: Optional[date] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    telefone_emergencia: Optional[str] = None
    telefone_emergencia_2: Optional[str] = None
    dados_bancarios: Optional[DadosBancarios] = None


class AniversarianteOut(BaseModel):
    nome: str
    data_aniversario: date
