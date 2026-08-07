from sqlalchemy.orm import Session

from app.models.departamento import Departamento
from app.models.log import Log
from app.models.user import User


def listar_departamentos(db: Session) -> list[Departamento]:
    return db.query(Departamento).order_by(Departamento.nome).all()


def contar_usuarios_por_departamento(db: Session, departamento_id: int) -> int:
    return db.query(User).filter(User.departamento_id == departamento_id).count()


def obter_departamento_por_id(db: Session, departamento_id: int) -> Departamento | None:
    return db.query(Departamento).filter(Departamento.id == departamento_id).first()


def obter_departamento_por_nome(db: Session, nome: str) -> Departamento | None:
    return db.query(Departamento).filter(Departamento.nome == nome).first()


def obter_departamento_por_nome_exceto_id(db: Session, nome: str, departamento_id: int) -> Departamento | None:
    return db.query(Departamento).filter(
        Departamento.nome == nome,
        Departamento.id != departamento_id,
    ).first()


def salvar_departamento_com_log(db: Session, departamento: Departamento, log: Log | None) -> Departamento:
    db.add(departamento)
    db.flush()
    if log is not None:
        db.add(log)
    db.commit()
    db.refresh(departamento)
    return departamento


def atualizar_departamento_com_log(db: Session, departamento: Departamento, log: Log | None) -> Departamento:
    if log is not None:
        db.add(log)
    db.commit()
    db.refresh(departamento)
    return departamento


def excluir_departamento_com_log(db: Session, departamento: Departamento, log: Log | None) -> None:
    db.query(User).filter(User.departamento_id == departamento.id).update({"departamento_id": None})
    if log is not None:
        db.add(log)
    db.delete(departamento)
    db.commit()
