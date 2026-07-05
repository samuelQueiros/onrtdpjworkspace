from datetime import datetime

from pydantic import BaseModel


class DocumentoOut(BaseModel):
    id: int
    user_id: int
    tipo: str
    nome_arquivo: str
    mime_type: str
    tamanho: int
    criado_por_nome: str
    criado_em: datetime


class MensagemOut(BaseModel):
    detail: str
