from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cargo import Cargo
from app.models.log import Log
from app.models.user import User


def listar_cargos(db: Session) -> list[Cargo]:
    return db.query(Cargo).order_by(Cargo.nome).all()


def obter_cargo_por_id(db: Session, cargo_id: int) -> Cargo | None:
    return db.query(Cargo).filter(Cargo.id == cargo_id).first()


def obter_cargo_por_nome(db: Session, nome: str) -> Cargo | None:
    return db.query(Cargo).filter(func.lower(Cargo.nome) == nome.lower()).first()


def obter_cargo_por_nome_exceto_id(db: Session, nome: str, cargo_id: int) -> Cargo | None:
    return db.query(Cargo).filter(func.lower(Cargo.nome) == nome.lower(), Cargo.id != cargo_id).first()


def contar_usuarios(db: Session, cargo_id: int) -> int:
    return db.query(User).filter(User.cargo_id == cargo_id).count()


def salvar_com_log(db: Session, cargo: Cargo, log: Log | None) -> Cargo:
    db.add(cargo)
    db.flush()
    if log is not None:
        db.add(log)
    db.commit()
    db.refresh(cargo)
    return cargo


def atualizar_com_log(db: Session, cargo: Cargo, log: Log | None) -> Cargo:
    if log is not None:
        db.add(log)
    db.commit()
    db.refresh(cargo)
    return cargo


def excluir_com_log(db: Session, cargo: Cargo, log: Log | None) -> None:
    db.query(User).filter(User.cargo_id == cargo.id).update({"cargo_id": None})
    if log is not None:
        db.add(log)
    db.delete(cargo)
    db.commit()
