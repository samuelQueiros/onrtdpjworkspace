from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import criar_token, get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.common import MensagemOut
from app.schemas.user import (
    AniversarianteOut,
    MeuPerfilOut,
    UserConfigUpdate,
    UserCreate,
    UserResponse,
    UserSensitiveResponse,
    UserUpdate,
)
from app.services import users_service

router = APIRouter(tags=["Usuarios"])


@router.get("/users", response_model=list[UserResponse])
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_admin)):
    return users_service.listar_usuarios(db)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return users_service.criar_usuario(db, payload, current_user)


@router.put("/users/{user_id}", response_model=UserResponse)
def editar_usuario(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return users_service.editar_usuario(db, user_id, payload, current_user)


@router.get("/users/{user_id}/dados-sensiveis", response_model=UserSensitiveResponse)
def dados_sensiveis_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return users_service.consultar_dados_sensiveis(db, user_id, current_user)


@router.get("/users/aniversariantes", response_model=list[AniversarianteOut])
def listar_aniversariantes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.listar_aniversariantes(db)


@router.delete("/users/{user_id}", response_model=MensagemOut, status_code=status.HTTP_200_OK)
def excluir_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users_service.desativar_usuario(db, user_id, current_user)
    return {"detail": "Usuario desativado com sucesso"}


@router.post("/users/{user_id}/reativar", response_model=UserResponse)
def reativar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return users_service.reativar_usuario(db, user_id, current_user)


@router.put("/me/configuracoes", response_model=UserResponse)
def atualizar_configuracoes(
    payload: UserConfigUpdate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resultado = users_service.atualizar_configuracoes(db, payload, current_user)
    senha_alterada = bool(payload.nova_senha and payload.nova_senha.strip())
    if senha_alterada:
        token = criar_token({
            "sub": str(current_user.id),
            "role": current_user.role,
            "nome": current_user.nome,
            "token_version": current_user.token_version,
        })
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            max_age=settings.access_token_expire_minutes * 60,
            path="/",
        )
    return resultado


@router.get("/users/me/perfil", response_model=MeuPerfilOut)
def meu_perfil(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.meu_perfil(db, current_user)
