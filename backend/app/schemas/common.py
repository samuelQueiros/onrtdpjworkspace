from pydantic import BaseModel


class MensagemOut(BaseModel):
    detail: str
