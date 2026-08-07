from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.schemas.configuracao import ConfiguracaoOut, ConfiguracaoUpdate
from app.services import configuracao_service

router = APIRouter(prefix="/configuracao", tags=["Configuração"])


@router.get("", response_model=ConfiguracaoOut)
def obter_configuracao(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return configuracao_service.formatar_configuracao(configuracao_service.obter_configuracao(db))


@router.put("", response_model=ConfiguracaoOut)
def atualizar_configuracao(
    payload: ConfiguracaoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return configuracao_service.atualizar_configuracao(db, payload, current_user)
