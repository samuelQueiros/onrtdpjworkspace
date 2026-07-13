from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user, limpar_falhas_login, registrar_falha_login, verificar_limite_login
from app.database import get_db
from app.models.user import User
from app.schemas.auth import AuthUserOut, TokenOut
from app.services.auth_service import autenticar_usuario, formatar_usuario_autenticado

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/login", response_model=TokenOut)
def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    chave = request.client.host if request.client else "desconhecido"
    verificar_limite_login(chave)
    try:
        resultado = autenticar_usuario(db, form_data.username, form_data.password)
    except Exception:
        registrar_falha_login(chave)
        raise
    limpar_falhas_login(chave)
    response.set_cookie(
        "access_token",
        resultado["access_token"],
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return resultado


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie("access_token", path="/")


@router.get("/me", response_model=AuthUserOut)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return formatar_usuario_autenticado(current_user, db)
