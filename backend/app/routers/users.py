from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.ferias import Ferias
from app.models.log import Log
from app.schemas.user import UserCreate, UserUpdate, UserConfigUpdate
from app.core.security import get_current_user, require_admin, hash_senha

router = APIRouter(tags=["Usuários"])


def calcular_dias_restantes(user: User, db: Session) -> int:
    total_usado = sum(f.dias_usados for f in db.query(Ferias).filter(Ferias.user_id == user.id).all())
    return user.dias_totais - total_usado


@router.get("/users")
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "role": u.role,
            "dias_totais": u.dias_totais,
            "dias_restantes": calcular_dias_restantes(u, db),
            "criado_em": u.criado_em,
        }
        for u in users
    ]


@router.post("/users", status_code=status.HTTP_201_CREATED)
def criar_usuario(payload: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo_user = User(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_senha(payload.senha),
        role=payload.role,
        dias_totais=payload.dias_totais,
    )
    db.add(novo_user)
    db.flush()

    log = Log(user_id=novo_user.id, acao="USUARIO_CRIADO", detalhes=f"Usuário {novo_user.nome} criado")
    db.add(log)
    db.commit()
    db.refresh(novo_user)

    return {
        "id": novo_user.id,
        "nome": novo_user.nome,
        "email": novo_user.email,
        "role": novo_user.role,
        "dias_totais": novo_user.dias_totais,
        "dias_restantes": novo_user.dias_totais,
        "criado_em": novo_user.criado_em,
    }


@router.put("/users/{user_id}")
def editar_usuario(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if payload.nome is not None:
        user.nome = payload.nome
    if payload.email is not None:
        if db.query(User).filter(User.email == payload.email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Email já em uso por outro usuário")
        user.email = payload.email
    if payload.dias_totais is not None:
        user.dias_totais = payload.dias_totais

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "role": user.role,
        "dias_totais": user.dias_totais,
        "dias_restantes": calcular_dias_restantes(user, db),
        "criado_em": user.criado_em,
    }


@router.put("/me/configuracoes")
def atualizar_configuracoes(
    payload: UserConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.nome is not None:
        current_user.nome = payload.nome
    if payload.email is not None:
        if db.query(User).filter(User.email == payload.email, User.id != current_user.id).first():
            raise HTTPException(status_code=400, detail="Email já em uso por outro usuário")
        current_user.email = payload.email

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email,
        "role": current_user.role,
        "dias_totais": current_user.dias_totais,
        "dias_restantes": calcular_dias_restantes(current_user, db),
    }
