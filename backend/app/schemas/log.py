from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LogOut(BaseModel):
    id: int
    user_id: Optional[int]
    acao: str
    detalhes: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True
