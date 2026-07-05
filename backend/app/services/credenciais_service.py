from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import criptografar_credencial, descriptografar_credencial
from app.models.credencial import Credencial
from app.repositories import credenciais_repository
from app.schemas.credencial import CredencialCreate, CredencialUpdate


def formatar_credencial(credencial: Credencial, incluir_senha: bool = False) -> dict:
    dados = {
        "id": credencial.id,
        "descricao": credencial.descricao,
        "email": credencial.email,
        "criado_em": credencial.criado_em,
        "atualizado_em": credencial.atualizado_em,
        "total_usuarios": len(credencial.usuarios),
    }

    if incluir_senha:
        dados["senha"] = descriptografar_credencial(credencial.senha)

    return dados


def buscar_credencial(db: Session, credencial_id: int) -> Credencial:
    credencial = credenciais_repository.obter_credencial_por_id(db, credencial_id)
    if not credencial:
        raise HTTPException(status_code=404, detail="Credencial nao encontrada")
    return credencial


def minhas_credenciais(db: Session, user_id: int) -> list[dict]:
    credenciais = credenciais_repository.listar_credenciais_por_usuario(db, user_id)
    return [formatar_credencial(c, incluir_senha=True) for c in credenciais]


def listar_credenciais(db: Session) -> list[dict]:
    credenciais = credenciais_repository.listar_credenciais(db)
    return [formatar_credencial(c) for c in credenciais]


def criar_credencial(db: Session, payload: CredencialCreate) -> dict:
    credencial = Credencial(
        descricao=payload.descricao,
        email=payload.email,
        senha=criptografar_credencial(payload.senha),
    )
    credenciais_repository.salvar_credencial(db, credencial)
    return formatar_credencial(credencial)


def editar_credencial(db: Session, credencial_id: int, payload: CredencialUpdate) -> dict:
    credencial = buscar_credencial(db, credencial_id)

    if payload.descricao is not None:
        credencial.descricao = payload.descricao
    if payload.email is not None:
        credencial.email = payload.email
    if payload.senha is not None and payload.senha.strip():
        credencial.senha = criptografar_credencial(payload.senha)

    credencial.atualizado_em = datetime.utcnow()
    credenciais_repository.salvar_credencial(db, credencial)
    return formatar_credencial(credencial)


def excluir_credencial(db: Session, credencial_id: int) -> None:
    credencial = buscar_credencial(db, credencial_id)
    credenciais_repository.excluir_credencial(db, credencial)


def usuarios_credencial(db: Session, credencial_id: int) -> list[dict]:
    credencial = buscar_credencial(db, credencial_id)
    ids_com_acesso = {u.id for u in credencial.usuarios}
    usuarios = credenciais_repository.listar_usuarios(db)

    return [
        {
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "tem_acesso": user.id in ids_com_acesso,
        }
        for user in usuarios
    ]


def salvar_permissoes(db: Session, credencial_id: int, user_ids: list[int]) -> None:
    buscar_credencial(db, credencial_id)
    credenciais_repository.substituir_permissoes(db, credencial_id, user_ids)
