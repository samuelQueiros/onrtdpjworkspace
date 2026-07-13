from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.cargo import CargoCreate, CargoOut, CargoUpdate
from app.schemas.common import MensagemOut
from app.services import cargos_service

router = APIRouter(prefix="/cargos", tags=["Cargos"])


@router.get("", response_model=list[CargoOut])
def listar_cargos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return cargos_service.listar_cargos(db)


@router.post("", response_model=CargoOut, status_code=status.HTTP_201_CREATED)
def criar_cargo(payload: CargoCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return cargos_service.criar_cargo(db, payload, current_user)


@router.put("/{cargo_id}", response_model=CargoOut)
def editar_cargo(cargo_id: int, payload: CargoUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return cargos_service.editar_cargo(db, cargo_id, payload, current_user)


@router.delete("/{cargo_id}", response_model=MensagemOut)
def excluir_cargo(cargo_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    cargos_service.excluir_cargo(db, cargo_id, current_user)
    return {"detail": "Cargo excluido com sucesso"}
