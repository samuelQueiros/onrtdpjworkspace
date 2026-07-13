from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.importacao import ImportacaoOut
from app.services import importacao_service

router = APIRouter(prefix="/importacao", tags=["Importacao"])


@router.post("/ferias", response_model=ImportacaoOut, status_code=status.HTTP_200_OK)
async def importar_ferias(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    conteudo = await file.read(importacao_service.MAX_IMPORT_SIZE + 1)
    if len(conteudo) > importacao_service.MAX_IMPORT_SIZE:
        raise HTTPException(status_code=400, detail="Planilha muito grande. Limite: 5 MB")
    return importacao_service.importar_ferias(db, file.filename, conteudo, current_user)


@router.post("/logs", response_model=ImportacaoOut, status_code=status.HTTP_200_OK)
async def importar_logs(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    conteudo = await file.read(importacao_service.MAX_IMPORT_SIZE + 1)
    if len(conteudo) > importacao_service.MAX_IMPORT_SIZE:
        raise HTTPException(status_code=400, detail="Planilha muito grande. Limite: 5 MB")
    return importacao_service.importar_logs(db, file.filename, conteudo, current_user)
