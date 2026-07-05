from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.bloqueio import BloqueioCreate, BloqueioOut, BloqueioUpdate, MensagemOut
from app.services import bloqueios_service

router = APIRouter(prefix="/bloqueios", tags=["Bloqueios de Datas"])


@router.get("", response_model=list[BloqueioOut])
def listar_bloqueios(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return bloqueios_service.listar_bloqueios(db)


@router.post("", response_model=BloqueioOut, status_code=status.HTTP_201_CREATED)
def criar_bloqueio(
    payload: BloqueioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return bloqueios_service.criar_bloqueio(db, payload, current_user)


@router.put("/{bloqueio_id}", response_model=BloqueioOut)
def editar_bloqueio(
    bloqueio_id: int,
    payload: BloqueioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return bloqueios_service.editar_bloqueio(db, bloqueio_id, payload, current_user)


@router.delete("/{bloqueio_id}", response_model=MensagemOut, status_code=status.HTTP_200_OK)
def excluir_bloqueio(
    bloqueio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    bloqueios_service.excluir_bloqueio(db, bloqueio_id, current_user)
    return {"detail": "Bloqueio excluido com sucesso"}
