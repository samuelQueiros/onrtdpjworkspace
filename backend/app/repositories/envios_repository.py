from sqlalchemy.orm import Session, selectinload

from app.models.envio import Envio, EnvioEvento


def _carregar_envio(query):
    return query.options(selectinload(Envio.eventos))


def obter_envio_por_id(db: Session, envio_id: int) -> Envio | None:
    return _carregar_envio(db.query(Envio)).filter(Envio.id == envio_id).first()


def obter_envio_por_alerta_id(db: Session, alerta_id: int) -> Envio | None:
    return db.query(Envio).filter(Envio.alerta_id == alerta_id).first()


def obter_envio_por_token(db: Session, token: str) -> Envio | None:
    return db.query(Envio).filter(Envio.token_rastreio == token).first()


def listar_envios(db: Session) -> list[Envio]:
    return _carregar_envio(db.query(Envio)).order_by(Envio.enviado_em.desc()).all()


def listar_envios_monitorando(db: Session) -> list[Envio]:
    return db.query(Envio).filter(Envio.status == "monitorando").order_by(Envio.enviado_em.asc()).all()


def salvar(db: Session, *objetos) -> None:
    for objeto in objetos:
        if objeto is not None:
            db.add(objeto)


def flush(db: Session) -> None:
    db.flush()


def commit(db: Session) -> None:
    db.commit()
