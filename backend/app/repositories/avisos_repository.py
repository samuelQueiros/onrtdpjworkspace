from datetime import date

from sqlalchemy.orm import Session

from app.models.aviso import Aviso
from app.models.log import Log


def listar_avisos_ativos(db: Session, hoje: date) -> list[Aviso]:
    return (
        db.query(Aviso)
        .filter(
            (Aviso.data_expiracao == None) | (Aviso.data_expiracao >= hoje)  # noqa: E711
        )
        .order_by(Aviso.fixado.desc(), Aviso.criado_em.desc())
        .all()
    )


def listar_todos_avisos(db: Session) -> list[Aviso]:
    return db.query(Aviso).order_by(Aviso.fixado.desc(), Aviso.criado_em.desc()).all()


def obter_aviso_por_id(db: Session, aviso_id: int) -> Aviso | None:
    return db.query(Aviso).filter(Aviso.id == aviso_id).first()


def salvar_aviso_com_log(db: Session, aviso: Aviso, log: Log) -> Aviso:
    db.add(aviso)
    db.flush()
    db.add(log)
    db.commit()
    db.refresh(aviso)
    return aviso


def atualizar_aviso_com_log(db: Session, aviso: Aviso, log: Log) -> Aviso:
    db.add(log)
    db.commit()
    db.refresh(aviso)
    return aviso


def excluir_aviso_com_log(db: Session, aviso: Aviso, log: Log) -> None:
    db.add(log)
    db.delete(aviso)
    db.commit()
