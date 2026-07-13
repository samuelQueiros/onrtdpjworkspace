from sqlalchemy.orm import Session, selectinload

from app.models.departamento import Departamento
from app.models.log import Log
from app.models.user import User
from app.models.ferias import Ferias


def listar_usuarios(db: Session) -> list[User]:
    return (
        db.query(User)
        .options(selectinload(User.departamento), selectinload(User.cargo))
        .order_by(User.nome)
        .all()
    )


def listar_usuarios_com_aniversario(db: Session) -> list[User]:
    return (
        db.query(User)
        .filter(User.data_aniversario.isnot(None), User.ativo.is_(True))
        .order_by(User.data_aniversario)
        .all()
    )


def listar_ferias_para_saldos(db: Session, user_ids: list[int]) -> list[Ferias]:
    if not user_ids:
        return []
    return (
        db.query(Ferias)
        .filter(
            Ferias.user_id.in_(user_ids),
            Ferias.ferias_acordo.is_(False),
            Ferias.status.in_(["aprovada", "pendente"]),
        )
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


def contar_administradores_ativos(db: Session) -> int:
    return db.query(User).filter(User.role == "admin", User.ativo.is_(True)).count()


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
