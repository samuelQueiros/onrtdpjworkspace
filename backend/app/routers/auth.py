from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    get_current_user,
    limpar_falhas_login,
    obter_ip_cliente,
    registrar_falha_login,
    verificar_limite_login,
)
from app.database import get_db
from app.models.user import User
from app.schemas.auth import AuthUserOut, SessionOut, TokenOut
from app.services.auth_service import autenticar_usuario, formatar_usuario_autenticado

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


def _autenticar_limitado(request: Request, form_data: OAuth2PasswordRequestForm, db: Session):
    ip = obter_ip_cliente(request)
    chave = f"{ip}|{form_data.username.strip().lower()}"
    verificar_limite_login(chave)
    try:
        resultado = autenticar_usuario(db, form_data.username, form_data.password)
    except HTTPException as exc:
        if exc.status_code == 401:
            registrar_falha_login(chave)
        raise
    limpar_falhas_login(chave)
    return resultado


@router.post("/login", response_model=TokenOut)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return _autenticar_limitado(request, form_data, db)


@router.post("/session", response_model=SessionOut)
def criar_sessao(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    resultado = _autenticar_limitado(request, form_data, db)
    response.set_cookie(
        "access_token",
        resultado["access_token"],
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return resultado


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie("access_token", path="/")


@router.post("/logout-all", status_code=204)
def logout_all(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.token_version += 1
    db.commit()
    response.delete_cookie("access_token", path="/")


@router.get("/me", response_model=AuthUserOut)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return formatar_usuario_autenticado(current_user, db)
