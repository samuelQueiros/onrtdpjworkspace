from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import criar_token, verificar_senha
from app.models.user import User
from app.repositories import auth_repository


def calcular_dias_restantes(user: User, db: Session) -> int:
    from app.services.ferias_service import calcular_saldo

    return calcular_saldo(db, user)


def formatar_usuario_autenticado(user: User, db: Session) -> dict:
    departamento = None
    if user.departamento_id:
        dep = auth_repository.obter_departamento_por_id(db, user.departamento_id)
        departamento = {"id": dep.id, "nome": dep.nome} if dep else None

    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "role": user.role,
        "dias_totais": user.dias_totais,
        "dias_restantes": calcular_dias_restantes(user, db),
        "departamento": departamento,
        "data_admissao": str(user.data_admissao) if user.data_admissao else None,
        "data_aniversario": str(user.data_aniversario) if user.data_aniversario else None,
    }


def autenticar_usuario(db: Session, email: str, senha: str) -> dict:
    user = auth_repository.obter_usuario_por_email(db, email)
    if not user or not verificar_senha(senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )

    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "nome": user.nome,
        "token_version": user.token_version,
    }
    return {
        "access_token": criar_token(token_data),
        "token_type": "bearer",
        "user": formatar_usuario_autenticado(user, db),
    }
