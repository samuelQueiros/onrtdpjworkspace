from datetime import datetime

from pydantic import BaseModel, EmailStr


class ConfiguracaoOut(BaseModel):
    email_destinatario: str
    atualizado_em: datetime

    class Config:
        from_attributes = True


class ConfiguracaoUpdate(BaseModel):
    email_destinatario: EmailStr
