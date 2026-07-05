from sqlalchemy.orm import Session

from app.models.ferias import Ferias
from app.models.log import Log
from app.models.user import User


def obter_usuario_por_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def existe_ferias_periodo(db: Session, user_id: int, data_inicio, data_fim) -> bool:
    return (
        db.query(Ferias)
        .filter(
            Ferias.user_id == user_id,
            Ferias.data_inicio == data_inicio,
            Ferias.data_fim == data_fim,
        )
        .first()
        is not None
    )


def adicionar_ferias(db: Session, ferias: Ferias) -> Ferias:
    db.add(ferias)
    return ferias


def adicionar_log(db: Session, log: Log) -> Log:
    db.add(log)
    return log


def commit(db: Session) -> None:
    db.commit()
