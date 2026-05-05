from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ferias import Ferias
from app.core.security import verificar_senha, criar_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def calcular_dias_restantes(user: User, db: Session) -> int:
    dias_usados = db.query(Ferias).filter(Ferias.user_id == user.id).all()
    total_usado = sum(f.dias_usados for f in dias_usados)
    return user.dias_totais - total_usado


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verificar_senha(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    token_data = {"sub": str(user.id), "role": user.role, "nome": user.nome}
    token = criar_token(token_data)
    dias_restantes = calcular_dias_restantes(user, db)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "role": user.role,
            "dias_totais": user.dias_totais,
            "dias_restantes": dias_restantes,
        },
    }


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dias_restantes = calcular_dias_restantes(current_user, db)
    return {
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email,
        "role": current_user.role,
        "dias_totais": current_user.dias_totais,
        "dias_restantes": dias_restantes,
    }
