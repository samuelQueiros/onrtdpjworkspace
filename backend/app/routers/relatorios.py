from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.schemas.relatorio import DashboardOut, LogDetalhadoOut, RelatorioColaboradoresOut
from app.services import relatorios_service

router = APIRouter(tags=["Relatorios e Logs"])


@router.get("/relatorios", response_model=RelatorioColaboradoresOut)
def relatorio_colaboradores(db: Session = Depends(get_db), _=Depends(require_admin)):
    return relatorios_service.relatorio_colaboradores(db)


@router.get("/dashboard", response_model=DashboardOut)
def dashboard_admin(db: Session = Depends(get_db), _=Depends(require_admin)):
    return relatorios_service.dashboard_admin(db)


@router.get("/logs", response_model=list[LogDetalhadoOut])
def listar_logs(db: Session = Depends(get_db), _=Depends(require_admin)):
    return relatorios_service.listar_logs(db)
