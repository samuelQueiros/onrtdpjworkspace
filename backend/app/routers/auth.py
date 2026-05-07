from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ferias import Ferias
from app.models.departamento import Departamento
from app.core.security import verificar_senha, criar_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def calcular_dias_restantes(user: User, db: Session) -> int:
    from app.routers.ferias import calcular_saldo
    return calcular_saldo(db, user)


def _fmt_user(user: User, db: Session) -> dict:
    dep = None
    if user.departamento_id:
        d = db.query(Departamento).filter(Departamento.id == user.departamento_id).first()
        dep = {"id": d.id, "nome": d.nome} if d else None

    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "role": user.role,
        "dias_totais": user.dias_totais,
        "dias_restantes": calcular_dias_restantes(user, db),
        "departamento": dep,
        "data_admissao": str(user.data_admissao) if user.data_admissao else None,
    }


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verificar_senha(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )

    token_data = {"sub": str(user.id), "role": user.role, "nome": user.nome}
    token = criar_token(token_data)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _fmt_user(user, db),
    }


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _fmt_user(current_user, db)
