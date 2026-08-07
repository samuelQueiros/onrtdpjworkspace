from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EnvioEventoOut(BaseModel):
    id: int
    tipo: str
    status_anterior: Optional[str]
    status_novo: Optional[str]
    detalhes: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True


class EnvioOut(BaseModel):
    id: int
    alerta_id: int
    colaborador_nome_snapshot: str
    periodo_ferias_snapshot: str
    destinatario_email_snapshot: str
    status: str
    erro_codigo: Optional[str]
    erro_mensagem: Optional[str]
    tentativas_verificacao: int
    enviado_em: datetime
    prazo_limite: datetime
    ultima_verificacao_em: Optional[datetime]
    lido_em: Optional[datetime]
    respondido_em: Optional[datetime]
    resposta_texto: Optional[str]
    eventos: list[EnvioEventoOut] = []

    class Config:
        from_attributes = True
