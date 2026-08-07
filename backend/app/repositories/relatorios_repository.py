from datetime import date

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.departamento import Departamento
from app.models.ferias import Ferias
from app.models.log import Log
from app.models.user import User
from app.models.patrimonio import SolicitacaoEquipamento


def listar_usuarios_ordenados(db: Session) -> list[User]:
    return db.query(User).filter(User.is_sistema.is_(False)).order_by(User.nome).all()


def listar_ferias_aprovadas_ciclo(db: Session, user_id: int, ciclo_inicio: date) -> list[Ferias]:
    return (
        db.query(Ferias)
        .filter(
            Ferias.user_id == user_id,
            Ferias.ferias_acordo == False,  # noqa: E712
            Ferias.status == "aprovada",
            Ferias.data_inicio >= ciclo_inicio,
        )
        .all()
    )


def listar_ferias_acordo_aprovadas(db: Session, user_id: int) -> list[Ferias]:
    return (
        db.query(Ferias)
        .filter(
            Ferias.user_id == user_id,
            Ferias.ferias_acordo == True,  # noqa: E712
            Ferias.status == "aprovada",
        )
        .all()
    )


def listar_ferias_pendentes_usuario(db: Session, user_id: int) -> list[Ferias]:
    return db.query(Ferias).filter(Ferias.user_id == user_id, Ferias.status == "pendente").all()


def contar_colaboradores(db: Session) -> int:
    return db.query(User).filter(User.role == "user").count()


def contar_ferias_por_status(db: Session, status: str) -> int:
    return (
        db.query(Ferias)
        .join(User, Ferias.user_id == User.id)
        .filter(Ferias.status == status, User.is_sistema.is_(False))
        .count()
    )


def contar_autorizacoes_equipamentos_por_status(db: Session, status: str) -> int:
    return db.query(SolicitacaoEquipamento).filter(SolicitacaoEquipamento.status == status).count()


def contar_departamentos(db: Session) -> int:
    return db.query(Departamento).count()


def listar_ferias_em_andamento(db: Session, hoje: date) -> list[Ferias]:
    return (
        db.query(Ferias)
        .join(User, Ferias.user_id == User.id)
        .filter(
            Ferias.status == "aprovada",
            Ferias.data_inicio <= hoje,
            Ferias.data_fim >= hoje,
            User.is_sistema.is_(False),
        )
        .all()
    )


def listar_proximas_ferias(db: Session, hoje: date, limite: date) -> list[Ferias]:
    return (
        db.query(Ferias)
        .join(User, Ferias.user_id == User.id)
        .filter(
            Ferias.status == "aprovada",
            Ferias.data_inicio > hoje,
            Ferias.data_inicio <= limite,
            User.is_sistema.is_(False),
        )
        .order_by(Ferias.data_inicio)
        .all()
    )


def listar_alertas_contabilidade(db: Session, hoje: date, limite: date) -> list[Ferias]:
    return (
        db.query(Ferias)
        .join(User, Ferias.user_id == User.id)
        .filter(
            Ferias.status == "aprovada",
            Ferias.data_inicio >= hoje,
            Ferias.data_inicio <= limite,
            User.is_sistema.is_(False),
        )
        .all()
    )


def _logs_visiveis(db: Session):
    return (
        db.query(Log)
        .outerjoin(User, Log.user_id == User.id)
        .filter(or_(User.id.is_(None), User.is_sistema.is_(False)))
    )


def listar_logs(db: Session, offset: int = 0, limit: int = 50) -> list[Log]:
    return _logs_visiveis(db).order_by(Log.criado_em.desc()).offset(offset).limit(limit).all()


def listar_todos_logs(db: Session) -> list[Log]:
    return _logs_visiveis(db).order_by(Log.criado_em.desc()).all()


def contar_logs(db: Session) -> int:
    return _logs_visiveis(db).count()
