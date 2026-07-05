from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.auth_service import autenticar_usuario, formatar_usuario_autenticado

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return autenticar_usuario(db, form_data.username, form_data.password)


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return formatar_usuario_autenticado(current_user, db)
