from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.credencial import (
    CredencialComSenhaOut,
    CredencialCreate,
    CredencialOut,
    CredencialUpdate,
    PermissoesUpdate,
)
from app.services import credenciais_service

router = APIRouter(prefix="/credenciais", tags=["Credenciais"])


@router.get("/minhas", response_model=List[CredencialComSenhaOut])
def minhas_credenciais(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return credenciais_service.minhas_credenciais(db, current_user.id)


@router.get("", response_model=List[CredencialOut])
def listar_credenciais(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return credenciais_service.listar_credenciais(db)


@router.post("", response_model=CredencialOut, status_code=status.HTTP_201_CREATED)
def criar_credencial(
    payload: CredencialCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return credenciais_service.criar_credencial(db, payload)


@router.put("/{credencial_id}", response_model=CredencialOut)
def editar_credencial(
    credencial_id: int,
    payload: CredencialUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return credenciais_service.editar_credencial(db, credencial_id, payload)


@router.delete("/{credencial_id}", status_code=status.HTTP_200_OK)
def excluir_credencial(
    credencial_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    credenciais_service.excluir_credencial(db, credencial_id)
    return {"detail": "Credencial excluida com sucesso"}


@router.get("/{credencial_id}/usuarios")
def usuarios_credencial(
    credencial_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return credenciais_service.usuarios_credencial(db, credencial_id)


@router.put("/{credencial_id}/permissoes", status_code=status.HTTP_200_OK)
def salvar_permissoes(
    credencial_id: int,
    payload: PermissoesUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    credenciais_service.salvar_permissoes(db, credencial_id, payload.user_ids)
    return {"detail": "Permissoes atualizadas com sucesso"}
