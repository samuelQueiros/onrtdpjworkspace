from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.common import MensagemOut
from app.schemas.user import AniversarianteOut, UserConfigUpdate, UserCreate, UserResponse, UserSensitiveResponse, UserUpdate
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
    _=Depends(require_admin),
):
    return users_service.formatar_dados_sensiveis(users_service.buscar_usuario(db, user_id))


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


@router.put("/me/configuracoes", response_model=UserResponse)
def atualizar_configuracoes(
    payload: UserConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.atualizar_configuracoes(db, payload, current_user)
