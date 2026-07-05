from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.schemas.alerta import AlertaOut
from app.schemas.common import MensagemOut
from app.services import alertas_service

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("", response_model=list[AlertaOut])
def listar_alertas(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return alertas_service.listar_alertas(db)


@router.put("/{alerta_id}/lido", response_model=MensagemOut)
def marcar_lido(
    alerta_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    alertas_service.marcar_lido(db, alerta_id)
    return {"detail": "Alerta marcado como lido"}


@router.put("/marcar-todos-lidos", response_model=MensagemOut)
def marcar_todos_lidos(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    alertas_service.marcar_todos_lidos(db)
    return {"detail": "Todos os alertas marcados como lidos"}
