from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.schemas.relatorio import DashboardOut, LogsPageOut, RelatorioColaboradoresOut
from app.services import relatorios_service

router = APIRouter(tags=["Relatorios e Logs"])


@router.get("/relatorios", response_model=RelatorioColaboradoresOut)
def relatorio_colaboradores(db: Session = Depends(get_db), _=Depends(require_admin)):
    return relatorios_service.relatorio_colaboradores(db)


@router.get("/relatorios/exportar")
def exportar_relatorio_colaboradores(db: Session = Depends(get_db), _=Depends(require_admin)):
    conteudo = relatorios_service.exportar_relatorio_colaboradores_xlsx(db)
    nome_arquivo = f"relatorio-ferias-{date.today().isoformat()}.xlsx"
    return StreamingResponse(
        BytesIO(conteudo),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )


@router.get("/dashboard", response_model=DashboardOut)
def dashboard_admin(db: Session = Depends(get_db), _=Depends(require_admin)):
    return relatorios_service.dashboard_admin(db)


@router.get("/logs", response_model=LogsPageOut)
def listar_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return relatorios_service.listar_logs(db, page, page_size)


@router.get("/logs/exportar")
def exportar_logs(db: Session = Depends(get_db), _=Depends(require_admin)):
    conteudo = relatorios_service.exportar_logs_xlsx(db)
    nome_arquivo = f"logs-sistema-{date.today().isoformat()}.xlsx"
    return StreamingResponse(
        BytesIO(conteudo),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )
