from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.common import MensagemOut
from app.schemas.ferias import (
    DisponibilidadeOut,
    FeriadoOut,
    FeriasAprovar,
    FeriasCreate,
    FeriasOut,
    FeriasUpdate,
    MinhasFeriasOut,
)
from app.services import ferias_service

router = APIRouter(prefix="/ferias", tags=["Ferias"])


@router.get("/feriados/{year}", response_model=list[FeriadoOut])
def listar_feriados(year: int, _=Depends(get_current_user)):
    return ferias_service.listar_feriados(year)


@router.get("/me", response_model=MinhasFeriasOut)
def minhas_ferias(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ferias_service.minhas_ferias(db, current_user)


@router.get("/pendentes", response_model=list[FeriasOut])
def ferias_pendentes(db: Session = Depends(get_db), _=Depends(require_admin)):
    return ferias_service.ferias_pendentes(db)


@router.get("/todas", response_model=list[FeriasOut])
def todas_ferias(db: Session = Depends(get_db), _=Depends(require_admin)):
    return ferias_service.todas_ferias(db)


@router.get("/disponibilidade", response_model=DisponibilidadeOut)
def disponibilidade(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ferias_service.disponibilidade(db, current_user)


@router.post("", response_model=FeriasOut, status_code=status.HTTP_201_CREATED)
def registrar_ferias(
    payload: FeriasCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ferias_service.registrar_ferias(db, payload, current_user)


@router.put("/{ferias_id}/aprovar", response_model=FeriasOut)
def aprovar_ferias(
    ferias_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return ferias_service.aprovar_ferias(db, ferias_id, current_user)


@router.put("/{ferias_id}/rejeitar", response_model=FeriasOut)
def rejeitar_ferias(
    ferias_id: int,
    payload: FeriasAprovar,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return ferias_service.rejeitar_ferias(db, ferias_id, payload, current_user)


@router.put("/{ferias_id}", response_model=FeriasOut)
def editar_ferias(
    ferias_id: int,
    payload: FeriasUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ferias_service.editar_ferias(db, ferias_id, payload, current_user)


@router.delete("/{ferias_id}", response_model=MensagemOut, status_code=status.HTTP_200_OK)
def cancelar_ferias(
    ferias_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ferias_service.cancelar_ferias(db, ferias_id, current_user)
    return {"detail": "Ferias canceladas com sucesso"}
