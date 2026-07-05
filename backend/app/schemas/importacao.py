from pydantic import BaseModel


class ImportacaoOut(BaseModel):
    inseridos: int
    erros: list[str]
    mensagem: str
