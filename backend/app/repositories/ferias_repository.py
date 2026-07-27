from sqlalchemy.orm import Session

from app.models.bloqueio import BloqueioData
from app.models.departamento import Departamento
from app.models.ferias import Ferias
from app.models.log import Log
from app.models.saldo_ferias import SaldoFeriasMovimento
from app.models.user import User


def obter_departamento_por_id(db: Session, departamento_id: int) -> Departamento | None:
    return db.query(Departamento).filter(Departamento.id == departamento_id).first()


def obter_user_por_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def listar_users_por_departamento(db: Session, departamento_id: int) -> list[User]:
    return db.query(User).filter(User.departamento_id == departamento_id).all()


def listar_ferias_por_usuario(db: Session, user_id: int) -> list[Ferias]:
    return db.query(Ferias).filter(Ferias.user_id == user_id).order_by(Ferias.criado_em.desc()).all()


def listar_ferias_pendentes(db: Session) -> list[Ferias]:
    return db.query(Ferias).filter(Ferias.status == "pendente").order_by(Ferias.criado_em.asc()).all()


def listar_todas_ferias(db: Session) -> list[Ferias]:
    return db.query(Ferias).order_by(Ferias.criado_em.desc()).all()


def listar_ferias_aprovadas(db: Session) -> list[Ferias]:
    return db.query(Ferias).filter(Ferias.status == "aprovada").order_by(Ferias.data_inicio).all()


def listar_ferias_para_saldo(db: Session, user_id: int, ciclo_inicio, ciclo_fim, excluir_ferias_id: int | None = None):
    query = db.query(Ferias).filter(
        Ferias.user_id == user_id,
        Ferias.ferias_acordo == False,  # noqa: E712
        Ferias.status.in_(["aprovada", "pendente"]),
        Ferias.data_inicio >= ciclo_inicio,
        Ferias.data_inicio <= ciclo_fim,
    )
    if excluir_ferias_id:
        query = query.filter(Ferias.id != excluir_ferias_id)
    return query.all()


def listar_ferias_para_saldo_total(db: Session, user_id: int, excluir_ferias_id: int | None = None):
    """Todas as ferias (de qualquer ciclo) que contam contra o saldo acumulado."""
    query = db.query(Ferias).filter(
        Ferias.user_id == user_id,
        Ferias.ferias_acordo == False,  # noqa: E712
        Ferias.status.in_(["aprovada", "pendente"]),
    )
    if excluir_ferias_id:
        query = query.filter(Ferias.id != excluir_ferias_id)
    return query.all()


def listar_ferias_para_saldo_desde(
    db: Session,
    user_id: int,
    desde,
    excluir_ferias_id: int | None = None,
):
    query = db.query(Ferias).filter(
        Ferias.user_id == user_id,
        Ferias.ferias_acordo.is_(False),
        Ferias.status.in_(["aprovada", "pendente"]),
        Ferias.criado_em >= desde,
    )
    if excluir_ferias_id:
        query = query.filter(Ferias.id != excluir_ferias_id)
    return query.all()


def listar_movimentos_saldo(db: Session, user_id: int) -> list[SaldoFeriasMovimento]:
    return (
        db.query(SaldoFeriasMovimento)
        .filter(SaldoFeriasMovimento.user_id == user_id)
        .order_by(SaldoFeriasMovimento.criado_em, SaldoFeriasMovimento.id)
        .all()
    )


def obter_movimento_por_chave(db: Session, chave: str) -> SaldoFeriasMovimento | None:
    return (
        db.query(SaldoFeriasMovimento)
        .filter(SaldoFeriasMovimento.chave_idempotencia == chave)
        .first()
    )


def listar_ferias_conflitantes(
    db: Session,
    user_id: int,
    data_inicio,
    data_fim,
    excluir_ferias_id: int | None = None,
):
    query = db.query(Ferias).filter(
        Ferias.data_inicio <= data_fim,
        Ferias.data_fim >= data_inicio,
        Ferias.status == "aprovada",
        Ferias.user_id != user_id,
    )
    if excluir_ferias_id:
        query = query.filter(Ferias.id != excluir_ferias_id)
    return query


def obter_bloqueio_sobreposto(db: Session, data_inicio, data_fim) -> BloqueioData | None:
    return (
        db.query(BloqueioData)
        .filter(
            BloqueioData.data_inicio <= data_fim,
            BloqueioData.data_fim >= data_inicio,
        )
        .first()
    )


def listar_bloqueios(db: Session) -> list[BloqueioData]:
    return db.query(BloqueioData).order_by(BloqueioData.data_inicio).all()


def obter_ferias_por_id(db: Session, ferias_id: int) -> Ferias | None:
    return db.query(Ferias).filter(Ferias.id == ferias_id).first()


def obter_ferias_por_id_para_atualizar(db: Session, ferias_id: int) -> Ferias | None:
    return db.query(Ferias).filter(Ferias.id == ferias_id).with_for_update().first()


def salvar_ferias_com_log(db: Session, ferias: Ferias, log: Log) -> Ferias:
    db.add(ferias)
    db.flush()
    db.add(log)
    db.commit()
    db.refresh(ferias)
    return ferias


def atualizar_ferias_com_log(db: Session, ferias: Ferias, log: Log) -> Ferias:
    db.add(log)
    db.commit()
    db.refresh(ferias)
    return ferias


def excluir_ferias_com_log(db: Session, ferias: Ferias, log: Log) -> None:
    db.delete(ferias)
    db.add(log)
    db.commit()
