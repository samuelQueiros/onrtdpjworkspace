from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.ficha_admissional import (
    FichaAdmissionalImportOut,
    FichaAdmissionalOut,
    FichaAdmissionalUpdate,
)
from app.schemas.historico_colaborador import HistoricoColaboradorOut
from app.schemas.historico_salarial import HistoricoSalarialOut
from app.services import fichas_admissionais_service, importacao_service


router = APIRouter(tags=["Fichas admissionais"])


# A rota /users/me/ficha-admissional precisa ser declarada ANTES das rotas
# /users/{user_id}/ficha-admissional: a ordem de registro determina a ordem de
# matching do FastAPI/Starlette. Somente leitura: o colaborador nao pode alterar
# a propria ficha admissional, apenas a administracao.
@router.get("/users/me/ficha-admissional", response_model=FichaAdmissionalOut | None)
def minha_ficha(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return fichas_admissionais_service.minha_ficha(db, current_user)


@router.get("/users/{user_id}/ficha-admissional", response_model=FichaAdmissionalOut | None)
def consultar_ficha(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return fichas_admissionais_service.consultar_ficha(db, user_id, current_user)


@router.put("/users/{user_id}/ficha-admissional", response_model=FichaAdmissionalOut)
def atualizar_ficha(
    user_id: int,
    payload: FichaAdmissionalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return fichas_admissionais_service.atualizar_ficha(db, user_id, payload, current_user)


@router.get("/users/{user_id}/historico-salarial", response_model=list[HistoricoSalarialOut])
def historico_salarial(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return fichas_admissionais_service.historico_salarial(db, user_id, current_user)


@router.get("/users/{user_id}/historico-funcional", response_model=list[HistoricoColaboradorOut])
def historico_funcional(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return fichas_admissionais_service.historico_funcional(db, user_id, current_user)


@router.get("/users/{user_id}/ficha-admissional/modelo")
def baixar_modelo(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    conteudo = fichas_admissionais_service.gerar_modelo_xlsx(db, user_id, current_user)
    return StreamingResponse(
        BytesIO(conteudo),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="modelo-ficha-admissional.xlsx"'},
    )


@router.post(
    "/users/{user_id}/ficha-admissional/importar",
    response_model=FichaAdmissionalImportOut,
)
async def importar_ficha(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    conteudo = await file.read(importacao_service.MAX_IMPORT_SIZE + 1)
    if len(conteudo) > importacao_service.MAX_IMPORT_SIZE:
        raise HTTPException(status_code=400, detail="Planilha muito grande. Limite: 5 MB")
    return fichas_admissionais_service.importar_xlsx(
        db,
        user_id,
        file.filename,
        conteudo,
        current_user,
    )
