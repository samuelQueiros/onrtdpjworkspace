from sqlalchemy.orm import Session, joinedload

from app.models.documento import Documento
from app.models.log import Log
from app.models.user import User

TIPOS_DOCUMENTOS_HISTORICO = (
    "atestado",
    "contracheque",
    "outro",
    "termo_equipamentos",
)


def obter_usuario_por_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def obter_documento_por_id(db: Session, doc_id: int) -> Documento | None:
    return db.query(Documento).filter(Documento.id == doc_id).first()


def listar_documentos_por_usuario(db: Session, user_id: int) -> list[Documento]:
    return (
        db.query(Documento)
        .filter(Documento.user_id == user_id)
        .order_by(Documento.criado_em.desc())
        .all()
    )


def _consulta_historico(
    db: Session,
    caixa: str,
    usuario_id: int,
    filtro_usuario_id: int | None = None,
):
    consulta = db.query(Documento)
    if caixa == "recebidos_pessoais":
        consulta = consulta.filter(
            Documento.destino_tipo == "usuario",
            Documento.destinatario_id == usuario_id,
        )
    elif caixa == "recebidos_administracao":
        consulta = consulta.filter(Documento.destino_tipo == "administracao")
    elif caixa == "enviados":
        consulta = consulta.filter(
            Documento.criado_por_id == usuario_id,
            Documento.tipo.in_(TIPOS_DOCUMENTOS_HISTORICO),
        )
    else:
        raise ValueError("Caixa de documentos inválida")

    if filtro_usuario_id is not None:
        consulta = consulta.filter(Documento.user_id == filtro_usuario_id)
    return consulta


def listar_historico_paginado(
    db: Session,
    caixa: str,
    usuario_id: int,
    filtro_usuario_id: int | None,
    offset: int,
    limit: int,
) -> list[Documento]:
    return (
        _consulta_historico(db, caixa, usuario_id, filtro_usuario_id)
        .options(
            joinedload(Documento.criado_por),
            joinedload(Documento.destinatario),
        )
        .order_by(Documento.criado_em.desc(), Documento.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def contar_historico(
    db: Session,
    caixa: str,
    usuario_id: int,
    filtro_usuario_id: int | None,
) -> int:
    return _consulta_historico(db, caixa, usuario_id, filtro_usuario_id).count()


def salvar_documento_com_log(db: Session, doc: Documento, log: Log) -> Documento:
    db.add(doc)
    db.flush()
    db.add(log)
    db.commit()
    db.refresh(doc)
    return doc


def excluir_documento_com_log(db: Session, doc: Documento, log: Log) -> None:
    db.add(log)
    db.delete(doc)
    db.commit()
