from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.credencial import Credencial
from app.models.credencial_usuario import CredencialUsuario
from app.schemas.credencial import (
    CredencialCreate,
    CredencialUpdate,
    CredencialOut,
    CredencialComSenhaOut,
    PermissoesUpdate,
)
from app.core.crypto import criptografar_credencial, descriptografar_credencial
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/credenciais", tags=["Credenciais"])


def _fmt_credencial(c: Credencial, incluir_senha: bool = False) -> dict:
    dados = {
        "id": c.id,
        "descricao": c.descricao,
        "email": c.email,
        "criado_em": c.criado_em,
        "atualizado_em": c.atualizado_em,
        "total_usuarios": len(c.usuarios),
    }

    if incluir_senha:
        dados["senha"] = descriptografar_credencial(c.senha)

    return dados


@router.get("/minhas", response_model=List[CredencialComSenhaOut])
def minhas_credenciais(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    credenciais = (
        db.query(Credencial)
        .join(CredencialUsuario, CredencialUsuario.credencial_id == Credencial.id)
        .filter(CredencialUsuario.user_id == current_user.id)
        .all()
    )
    return [_fmt_credencial(c, incluir_senha=True) for c in credenciais]


@router.get("", response_model=List[CredencialOut])
def listar_credenciais(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    credenciais = db.query(Credencial).order_by(Credencial.descricao).all()
    return [_fmt_credencial(c) for c in credenciais]


@router.post("", response_model=CredencialOut, status_code=status.HTTP_201_CREATED)
def criar_credencial(
    payload: CredencialCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    credencial = Credencial(
        descricao=payload.descricao,
        email=payload.email,
        senha=criptografar_credencial(payload.senha),
    )
    db.add(credencial)
    db.commit()
    db.refresh(credencial)
    return _fmt_credencial(credencial)


@router.put("/{credencial_id}", response_model=CredencialOut)
def editar_credencial(
    credencial_id: int,
    payload: CredencialUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    credencial = db.query(Credencial).filter(Credencial.id == credencial_id).first()
    if not credencial:
        raise HTTPException(status_code=404, detail="Credencial não encontrada")

    if payload.descricao is not None:
        credencial.descricao = payload.descricao
    if payload.email is not None:
        credencial.email = payload.email
    if payload.senha is not None and payload.senha.strip():
        credencial.senha = criptografar_credencial(payload.senha)

    credencial.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(credencial)
    return _fmt_credencial(credencial)


@router.delete("/{credencial_id}", status_code=status.HTTP_200_OK)
def excluir_credencial(
    credencial_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    credencial = db.query(Credencial).filter(Credencial.id == credencial_id).first()
    if not credencial:
        raise HTTPException(status_code=404, detail="Credencial não encontrada")

    db.delete(credencial)
    db.commit()
    return {"detail": "Credencial excluída com sucesso"}


@router.get("/{credencial_id}/usuarios")
def usuarios_credencial(
    credencial_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    credencial = db.query(Credencial).filter(Credencial.id == credencial_id).first()
    if not credencial:
        raise HTTPException(status_code=404, detail="Credencial não encontrada")

    ids_com_acesso = {u.id for u in credencial.usuarios}
    todos = db.query(User).order_by(User.nome).all()

    return [
        {
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "tem_acesso": u.id in ids_com_acesso,
        }
        for u in todos
    ]


@router.put("/{credencial_id}/permissoes", status_code=status.HTTP_200_OK)
def salvar_permissoes(
    credencial_id: int,
    payload: PermissoesUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    credencial = db.query(Credencial).filter(Credencial.id == credencial_id).first()
    if not credencial:
        raise HTTPException(status_code=404, detail="Credencial não encontrada")

    db.query(CredencialUsuario).filter(
        CredencialUsuario.credencial_id == credencial_id
    ).delete()

    for user_id in payload.user_ids:
        db.add(CredencialUsuario(credencial_id=credencial_id, user_id=user_id))

    db.commit()
    return {"detail": "Permissões atualizadas com sucesso"}
