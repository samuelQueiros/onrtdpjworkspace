from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: Optional[str] = "user"
    dias_totais: Optional[int] = 30


class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    dias_totais: Optional[int] = None


class UserConfigUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None


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
