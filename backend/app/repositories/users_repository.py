from sqlalchemy.orm import Session

from app.models.departamento import Departamento
from app.models.log import Log
from app.models.user import User


def listar_usuarios(db: Session) -> list[User]:
    return db.query(User).order_by(User.nome).all()


def listar_usuarios_com_aniversario(db: Session) -> list[User]:
    return (
        db.query(User)
        .filter(User.data_aniversario.isnot(None))
        .order_by(User.data_aniversario)
        .all()
    )


def obter_usuario_por_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def obter_usuario_por_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def obter_usuario_por_email_exceto_id(db: Session, email: str, user_id: int) -> User | None:
    return db.query(User).filter(User.email == email, User.id != user_id).first()


def obter_departamento_por_id(db: Session, departamento_id: int) -> Departamento | None:
    return db.query(Departamento).filter(Departamento.id == departamento_id).first()


def salvar_usuario_com_log(db: Session, user: User, log: Log) -> User:
    db.add(user)
    db.flush()
    if log.user_id is None:
        log.user_id = user.id
    db.add(log)
    db.commit()
    db.refresh(user)
    return user


def atualizar_usuario_com_log(db: Session, user: User, log: Log) -> User:
    db.add(log)
    db.commit()
    db.refresh(user)
    return user


def excluir_usuario_com_log(db: Session, user: User, log: Log) -> None:
    db.add(log)
    db.delete(user)
    db.commit()


def salvar_usuario(db: Session, user: User) -> User:
    db.commit()
    db.refresh(user)
    return user
