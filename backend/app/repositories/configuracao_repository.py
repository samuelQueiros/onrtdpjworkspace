from sqlalchemy.orm import Session

from app.models.configuracao import Configuracao
from app.models.log import Log


def obter_configuracao(db: Session) -> Configuracao | None:
    return db.query(Configuracao).filter(Configuracao.id == 1).first()


def salvar_configuracao_com_log(db: Session, configuracao: Configuracao, log: Log | None) -> Configuracao:
    db.add(configuracao)
    db.flush()
    if log is not None:
        db.add(log)
    db.commit()
    db.refresh(configuracao)
    return configuracao
