from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import criptografar_credencial, descriptografar_credencial
from app.core.security import (
    limpar_falhas_login,
    registrar_falha_login,
    verificar_limite_login,
    verificar_senha,
)
from app.models.credencial import Credencial
from app.models.user import User
from app.repositories import credenciais_repository
from app.schemas.credencial import CredencialCreate, CredencialUpdate
from app.services import log_service


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
        raise HTTPException(status_code=404, detail="Credencial não encontrada")
    return credencial


def minhas_credenciais(
    db: Session,
    user_id: int,
    current_user: User | None = None,
) -> list[dict]:
    credenciais = credenciais_repository.listar_credenciais_por_usuario(db, user_id)
    return [formatar_credencial(c) for c in credenciais]


def revelar_credencial(
    db: Session,
    credencial_id: int,
    senha_atual: str,
    current_user: User,
) -> dict:
    credencial = buscar_credencial(db, credencial_id)
    autorizado = current_user.role == "admin" or credenciais_repository.usuario_tem_acesso(
        db,
        credencial_id,
        current_user.id,
    )
    if not autorizado:
        raise HTTPException(status_code=404, detail="Credencial não encontrada")
    chave_limite = f"reveal:{current_user.id}"
    verificar_limite_login(chave_limite)
    if not verificar_senha(senha_atual, current_user.senha_hash):
        registrar_falha_login(chave_limite)
        raise HTTPException(status_code=401, detail="Senha atual incorreta")
    limpar_falhas_login(chave_limite)

    senha = descriptografar_credencial(credencial.senha)
    log = log_service.construir_log(
        current_user,
        acao="CREDENCIAL_REVELADA",
        detalhes=f"Credencial #{credencial_id} revelada pelo usuário",
    )
    if log is not None:
        db.add(log)
    db.commit()
    return {"id": credencial.id, "senha": senha}


def listar_credenciais(db: Session) -> list[dict]:
    credenciais = credenciais_repository.listar_credenciais(db)
    return [formatar_credencial(c) for c in credenciais]


def criar_credencial(
    db: Session,
    payload: CredencialCreate,
    current_user: User | None = None,
) -> dict:
    credencial = Credencial(
        descricao=payload.descricao,
        email=payload.email,
        senha=criptografar_credencial(payload.senha),
    )
    if current_user is not None:
        log = log_service.construir_log(
            current_user,
            acao="CREDENCIAL_CRIADA",
            detalhes=f"Credencial '{payload.descricao}' criada",
        )
        if log is not None:
            db.add(log)
    credenciais_repository.salvar_credencial(db, credencial)
    return formatar_credencial(credencial)


def editar_credencial(
    db: Session,
    credencial_id: int,
    payload: CredencialUpdate,
    current_user: User | None = None,
) -> dict:
    credencial = buscar_credencial(db, credencial_id)

    if payload.descricao is not None:
        credencial.descricao = payload.descricao
    if payload.email is not None:
        credencial.email = payload.email
    if payload.senha is not None and payload.senha.strip():
        credencial.senha = criptografar_credencial(payload.senha)

    credencial.atualizado_em = datetime.utcnow()
    if current_user is not None:
        log = log_service.construir_log(
            current_user,
            acao="CREDENCIAL_EDITADA",
            detalhes=f"Credencial #{credencial_id} editada",
        )
        if log is not None:
            db.add(log)
    credenciais_repository.salvar_credencial(db, credencial)
    return formatar_credencial(credencial)


def excluir_credencial(
    db: Session,
    credencial_id: int,
    current_user: User | None = None,
) -> None:
    credencial = buscar_credencial(db, credencial_id)
    if current_user is not None:
        log = log_service.construir_log(
            current_user,
            acao="CREDENCIAL_EXCLUIDA",
            detalhes=f"Credencial #{credencial_id} ('{credencial.descricao}') excluída",
        )
        if log is not None:
            db.add(log)
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


def salvar_permissoes(
    db: Session,
    credencial_id: int,
    user_ids: list[int],
    current_user: User | None = None,
) -> None:
    buscar_credencial(db, credencial_id)
    ids_unicos = sorted(set(user_ids))
    usuarios_validos = {
        user.id for user in credenciais_repository.listar_usuarios(db)
        if user.ativo
    }
    invalidos = sorted(set(ids_unicos) - usuarios_validos)
    if invalidos:
        raise HTTPException(
            status_code=400,
            detail=f"Usuários inválidos ou inativos: {', '.join(map(str, invalidos))}",
        )
    if current_user is not None:
        log = log_service.construir_log(
            current_user,
            acao="CREDENCIAL_PERMISSOES_ATUALIZADAS",
            detalhes=(
                f"Permissões da credencial #{credencial_id} atualizadas "
                f"para {len(ids_unicos)} usuário(s)"
            ),
        )
        if log is not None:
            db.add(log)
    credenciais_repository.substituir_permissoes(db, credencial_id, ids_unicos)
