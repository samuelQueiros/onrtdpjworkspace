from sqlalchemy.orm import Session

from app.models.bloqueio import BloqueioData
from app.models.log import Log


def listar_bloqueios(db: Session) -> list[BloqueioData]:
    return db.query(BloqueioData).order_by(BloqueioData.data_inicio).all()


def obter_bloqueio_por_id(db: Session, bloqueio_id: int) -> BloqueioData | None:
    return db.query(BloqueioData).filter(BloqueioData.id == bloqueio_id).first()


def salvar_bloqueio_com_log(db: Session, bloqueio: BloqueioData, log: Log | None) -> BloqueioData:
    db.add(bloqueio)
    db.flush()
    if log is not None:
        db.add(log)
    db.commit()
    db.refresh(bloqueio)
    return bloqueio


def atualizar_bloqueio_com_log(db: Session, bloqueio: BloqueioData, log: Log | None) -> BloqueioData:
    if log is not None:
        db.add(log)
    db.commit()
    db.refresh(bloqueio)
    return bloqueio


def excluir_bloqueio_com_log(db: Session, bloqueio: BloqueioData, log: Log | None) -> None:
    if log is not None:
        db.add(log)
    db.delete(bloqueio)
    db.commit()
