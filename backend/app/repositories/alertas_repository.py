from datetime import date

from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.ferias import Ferias


def listar_ferias_aprovadas_por_data_inicio(db: Session, data_inicio: date) -> list[Ferias]:
    return (
        db.query(Ferias)
        .filter(Ferias.data_inicio == data_inicio, Ferias.status == "aprovada")
        .all()
    )


def existe_alerta_por_ferias_e_tipo(db: Session, ferias_id: int, tipo: str) -> bool:
    return (
        db.query(Alerta)
        .filter(
            Alerta.ferias_id == ferias_id,
            Alerta.tipo == tipo,
        )
        .first()
        is not None
    )


def adicionar_alerta(db: Session, alerta: Alerta) -> Alerta:
    db.add(alerta)
    return alerta


def salvar_alertas(db: Session) -> None:
    db.commit()


def listar_alertas(db: Session) -> list[Alerta]:
    return db.query(Alerta).order_by(Alerta.lido.asc(), Alerta.criado_em.desc()).all()


def obter_alerta_por_id(db: Session, alerta_id: int) -> Alerta | None:
    return db.query(Alerta).filter(Alerta.id == alerta_id).first()


def marcar_alerta_lido(db: Session, alerta: Alerta) -> Alerta:
    alerta.lido = True
    db.commit()
    db.refresh(alerta)
    return alerta


def marcar_todos_lidos(db: Session) -> int:
    total = db.query(Alerta).filter(Alerta.lido == False).update({"lido": True})  # noqa: E712
    db.commit()
    return total
