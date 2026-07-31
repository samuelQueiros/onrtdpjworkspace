from sqlalchemy.orm import Session

from app.models.credencial import Credencial
from app.models.credencial_usuario import CredencialUsuario
from app.models.user import User


def listar_credenciais(db: Session) -> list[Credencial]:
    return db.query(Credencial).order_by(Credencial.descricao).all()


def listar_credenciais_por_usuario(db: Session, user_id: int) -> list[Credencial]:
    return (
        db.query(Credencial)
        .join(CredencialUsuario, CredencialUsuario.credencial_id == Credencial.id)
        .filter(CredencialUsuario.user_id == user_id)
        .all()
    )


def obter_credencial_por_id(db: Session, credencial_id: int) -> Credencial | None:
    return db.query(Credencial).filter(Credencial.id == credencial_id).first()


def usuario_tem_acesso(db: Session, credencial_id: int, user_id: int) -> bool:
    return (
        db.query(CredencialUsuario)
        .filter(
            CredencialUsuario.credencial_id == credencial_id,
            CredencialUsuario.user_id == user_id,
        )
        .first()
        is not None
    )


def salvar_credencial(db: Session, credencial: Credencial) -> Credencial:
    db.add(credencial)
    db.commit()
    db.refresh(credencial)
    return credencial


def excluir_credencial(db: Session, credencial: Credencial) -> None:
    db.delete(credencial)
    db.commit()


def listar_usuarios(db: Session) -> list[User]:
    return db.query(User).order_by(User.nome).all()


def substituir_permissoes(db: Session, credencial_id: int, user_ids: list[int]) -> None:
    db.query(CredencialUsuario).filter(
        CredencialUsuario.credencial_id == credencial_id
    ).delete()

    for user_id in user_ids:
        db.add(CredencialUsuario(credencial_id=credencial_id, user_id=user_id))

    db.commit()
