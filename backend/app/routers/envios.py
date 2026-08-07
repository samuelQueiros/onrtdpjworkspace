from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.schemas.envio import EnvioOut
from app.services import envios_service

router = APIRouter(prefix="/envios", tags=["Lembretes de Férias"])


@router.get("", response_model=list[EnvioOut])
def listar_envios(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return envios_service.listar_envios(db)


@router.post("/{alerta_id}/enviar", response_model=EnvioOut, status_code=201)
def enviar_lembrete(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return envios_service.enviar_lembrete(db, alerta_id, current_user)
