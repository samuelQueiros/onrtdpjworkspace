from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.departamento import Departamento
from app.models.ferias import Ferias
from app.models.log import Log
from app.models.saldo_ferias import SaldoFeriasMovimento
from app.models.user import User


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


def resumir_saldos_usuarios(db: Session, user_ids: list[int]) -> dict[int, dict[str, int]]:
    if not user_ids:
        return {}

    movimentos = (
        db.query(
            SaldoFeriasMovimento.user_id.label("user_id"),
            func.sum(SaldoFeriasMovimento.quantidade_dias).label("dias_direito_total"),
            func.min(SaldoFeriasMovimento.criado_em).label("marco"),
        )
        .filter(SaldoFeriasMovimento.user_id.in_(user_ids))
        .group_by(SaldoFeriasMovimento.user_id)
        .subquery()
    )
    ferias_usadas = (
        db.query(
            Ferias.user_id.label("user_id"),
            func.coalesce(func.sum(Ferias.dias_usados), 0).label("dias_usados_total"),
        )
        .join(movimentos, movimentos.c.user_id == Ferias.user_id)
        .filter(
            Ferias.ferias_acordo.is_(False),
            Ferias.status.in_(["aprovada", "pendente"]),
            Ferias.criado_em >= movimentos.c.marco,
        )
        .group_by(Ferias.user_id)
        .subquery()
    )
    linhas = (
        db.query(
            movimentos.c.user_id,
            movimentos.c.dias_direito_total,
            func.coalesce(ferias_usadas.c.dias_usados_total, 0),
        )
        .outerjoin(ferias_usadas, ferias_usadas.c.user_id == movimentos.c.user_id)
        .all()
    )
    return {
        user_id: {
            "saldo": int(dias_direito_total or 0) - int(dias_usados_total or 0),
            "dias_usados_total": int(dias_usados_total or 0),
        }
        for user_id, dias_direito_total, dias_usados_total in linhas
    }


def obter_usuario_por_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def obter_usuario_por_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(func.lower(User.email) == email.lower()).first()


def obter_usuario_por_email_exceto_id(db: Session, email: str, user_id: int) -> User | None:
    return db.query(User).filter(func.lower(User.email) == email.lower(), User.id != user_id).first()


def obter_usuario_por_cpf_hash(db: Session, cpf_hash: str, excluir_user_id: int | None = None) -> User | None:
    query = db.query(User).filter(User.cpf_hash == cpf_hash)
    if excluir_user_id is not None:
        query = query.filter(User.id != excluir_user_id)
    return query.first()


def obter_departamento_por_id(db: Session, departamento_id: int) -> Departamento | None:
    return db.query(Departamento).filter(Departamento.id == departamento_id).first()


def contar_administradores_ativos(db: Session) -> int:
    return db.query(User).filter(User.role == "admin", User.ativo.is_(True)).count()


def salvar_usuario_com_log(db: Session, user: User, log: Log, commit: bool = True) -> User:
    db.add(user)
    db.flush()
    if log.user_id is None:
        log.user_id = user.id
    db.add(log)
    if commit:
        db.commit()
        db.refresh(user)
    return user


def atualizar_usuario_com_log(db: Session, user: User, log: Log, commit: bool = True) -> User:
    db.add(log)
    if commit:
        db.commit()
        db.refresh(user)
    return user


def salvar_usuario(db: Session, user: User, commit: bool = True) -> User:
    db.add(user)
    if commit:
        db.commit()
        db.refresh(user)
    return user
