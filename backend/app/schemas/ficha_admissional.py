from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class FichaAdmissionalUpdate(BaseModel):
    local_nascimento: str | None = Field(default=None, max_length=150)
    uf_nascimento: str | None = Field(default=None, max_length=2)
    nacionalidade: str | None = Field(default=None, max_length=100)
    sexo: Literal["feminino", "masculino", "outro", "nao_informado"] | None = None
    nome_mae: str | None = Field(default=None, max_length=150)
    nome_pai: str | None = Field(default=None, max_length=150)

    pis_numero: str | None = Field(default=None, max_length=30)
    pis_emissao: date | None = None
    rg_numero: str | None = Field(default=None, max_length=30)
    rg_emissao: date | None = None
    rg_orgao_emissor: str | None = Field(default=None, max_length=50)
    ctps_numero: str | None = Field(default=None, max_length=30)
    ctps_serie: str | None = Field(default=None, max_length=30)
    ctps_validade: date | None = None
    ctps_uf: str | None = Field(default=None, max_length=2)
    ctps_emissao: date | None = None

    telefone_alternativo: str | None = Field(default=None, max_length=30)
    email_alternativo: EmailStr | None = None
    endereco_uf: str | None = Field(default=None, max_length=2)
    estado_civil: Literal[
        "solteiro",
        "casado",
        "divorciado",
        "viuvo",
        "separado",
        "uniao_estavel",
        "outro",
    ] | None = None
    nome_conjuge: str | None = Field(default=None, max_length=150)
    grau_instrucao: str | None = Field(default=None, max_length=120)

    salario: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    horario_trabalho: str | None = Field(default=None, max_length=150)
    dias_semana: str | None = Field(default=None, max_length=100)
    vale_transporte: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    beneficios: str | None = Field(default=None, max_length=300)
    valor_beneficios: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    contrato_experiencia_dias: int | None = Field(default=None, ge=0, le=365)
    status: Literal["rascunho", "completa"] = "rascunho"

    motivo_alteracao_salario: str | None = Field(default=None, max_length=300)
    tipo_alteracao_salario: Literal["reajuste", "correcao"] | None = None
    motivo_alteracao_beneficios: str | None = Field(default=None, max_length=300)
    tipo_alteracao_beneficios: Literal["real", "correcao"] | None = None

    @field_validator(
        "local_nascimento",
        "nacionalidade",
        "nome_mae",
        "nome_pai",
        "pis_numero",
        "rg_numero",
        "rg_orgao_emissor",
        "ctps_numero",
        "ctps_serie",
        "telefone_alternativo",
        "nome_conjuge",
        "grau_instrucao",
        "horario_trabalho",
        "dias_semana",
        "beneficios",
        "motivo_alteracao_salario",
        "motivo_alteracao_beneficios",
        mode="before",
    )
    @classmethod
    def normalizar_textos(cls, valor):
        if valor is None:
            return None
        texto = " ".join(str(valor).split())
        return texto or None

    @field_validator("uf_nascimento", "ctps_uf", "endereco_uf", mode="before")
    @classmethod
    def normalizar_uf(cls, valor):
        if valor is None or str(valor).strip() == "":
            return None
        texto = str(valor).strip().upper()
        if len(texto) != 2 or not texto.isalpha():
            raise ValueError("UF deve conter duas letras")
        return texto


class FichaAdmissionalOut(FichaAdmissionalUpdate):
    id: int
    user_id: int
    criado_por_id: int | None = None
    atualizado_por_id: int | None = None
    criado_em: datetime
    atualizado_em: datetime


class FichaAdmissionalImportOut(BaseModel):
    mensagem: str
    ficha: FichaAdmissionalOut
