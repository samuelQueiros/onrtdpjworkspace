from sqlalchemy.orm import Session

from app.models.documento import Documento
from app.models.log import Log
from app.models.user import User


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
