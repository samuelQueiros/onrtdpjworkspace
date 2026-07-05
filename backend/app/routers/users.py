from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserConfigUpdate, UserCreate, UserUpdate
from app.services import users_service

router = APIRouter(tags=["Usuarios"])


@router.get("/users")
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_admin)):
    return users_service.listar_usuarios(db)


@router.post("/users", status_code=status.HTTP_201_CREATED)
def criar_usuario(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return users_service.criar_usuario(db, payload, current_user)


@router.put("/users/{user_id}")
def editar_usuario(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return users_service.editar_usuario(db, user_id, payload, current_user)


@router.get("/users/aniversariantes")
def listar_aniversariantes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.listar_aniversariantes(db)


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def excluir_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users_service.excluir_usuario(db, user_id, current_user)
    return {"detail": "Usuario excluido com sucesso"}


@router.put("/me/configuracoes")
def atualizar_configuracoes(
    payload: UserConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.atualizar_configuracoes(db, payload, current_user)
