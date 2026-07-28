from datetime import datetime

from pydantic import BaseModel


class DocumentoOut(BaseModel):
    id: int
    user_id: int
    tipo: str
    nome_arquivo: str
    mime_type: str
    tamanho: int
    criado_por_id: int
    criado_por_nome: str
    destino_tipo: str
    destinatario_id: int | None
    destinatario_nome: str
    criado_em: datetime


class HistoricoDocumentosOut(BaseModel):
    recebidos_pessoais: list[DocumentoOut]
    recebidos_administracao: list[DocumentoOut]
    enviados: list[DocumentoOut]
