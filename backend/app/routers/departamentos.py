from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.departamento import (
    DepartamentoComTotalOut,
    DepartamentoCreate,
    DepartamentoOut,
    DepartamentoUpdate,
    MensagemOut,
)
from app.services import departamentos_service

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


@router.get("", response_model=list[DepartamentoComTotalOut])
def listar_departamentos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return departamentos_service.listar_departamentos(db)


@router.post("", response_model=DepartamentoOut, status_code=status.HTTP_201_CREATED)
def criar_departamento(
    payload: DepartamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return departamentos_service.criar_departamento(db, payload, current_user)


@router.put("/{dep_id}", response_model=DepartamentoOut)
def editar_departamento(
    dep_id: int,
    payload: DepartamentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return departamentos_service.editar_departamento(db, dep_id, payload, current_user)


@router.delete("/{dep_id}", response_model=MensagemOut, status_code=status.HTTP_200_OK)
def excluir_departamento(
    dep_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    departamentos_service.excluir_departamento(db, dep_id, current_user)
    return {"detail": "Departamento excluido com sucesso"}
