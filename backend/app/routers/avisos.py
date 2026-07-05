from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.aviso import AvisoCreate, AvisoOut, AvisoUpdate
from app.schemas.common import MensagemOut
from app.services import avisos_service

router = APIRouter(prefix="/avisos", tags=["Mural de Avisos"])


@router.get("", response_model=list[AvisoOut])
def listar_avisos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return avisos_service.listar_avisos(db)


@router.get("/todos", response_model=list[AvisoOut])
def listar_todos_avisos(db: Session = Depends(get_db), _=Depends(require_admin)):
    return avisos_service.listar_todos_avisos(db)


@router.post("", response_model=AvisoOut, status_code=status.HTTP_201_CREATED)
def criar_aviso(
    payload: AvisoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return avisos_service.criar_aviso(db, payload, current_user)


@router.put("/{aviso_id}", response_model=AvisoOut)
def editar_aviso(
    aviso_id: int,
    payload: AvisoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return avisos_service.editar_aviso(db, aviso_id, payload, current_user)


@router.delete("/{aviso_id}", response_model=MensagemOut, status_code=status.HTTP_200_OK)
def excluir_aviso(
    aviso_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    avisos_service.excluir_aviso(db, aviso_id, current_user)
    return {"detail": "Aviso excluido com sucesso"}
