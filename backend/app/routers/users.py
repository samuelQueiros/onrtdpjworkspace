from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.user import User
from app.models.ferias import Ferias
from app.models.log import Log
from app.models.departamento import Departamento
from app.schemas.user import UserCreate, UserUpdate, UserConfigUpdate
from app.core.security import get_current_user, require_admin, hash_senha, verificar_senha

router = APIRouter(tags=["Usuários"])


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
        "departamento_id": user.departamento_id,
        "departamento": dep,
        "data_admissao": user.data_admissao,
        "data_aniversario": user.data_aniversario,
        "criado_em": user.criado_em,
    }


@router.get("/users")
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(User).order_by(User.nome).all()
    return [_fmt_user(u, db) for u in users]


@router.post("/users", status_code=status.HTTP_201_CREATED)
def criar_usuario(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    if payload.departamento_id:
        if not db.query(Departamento).filter(Departamento.id == payload.departamento_id).first():
            raise HTTPException(status_code=404, detail="Departamento não encontrado")

    novo_user = User(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_senha(payload.senha),
        role=payload.role,
        dias_totais=payload.dias_totais,
        departamento_id=payload.departamento_id,
        data_admissao=payload.data_admissao,
        data_aniversario=payload.data_aniversario,
    )
    db.add(novo_user)
    db.flush()

    log = Log(
        user_id=novo_user.id,
        acao="USUARIO_CRIADO",
        detalhes=f"Usuário {novo_user.nome} ({novo_user.email}) criado por {current_user.nome}",
    )
    db.add(log)
    db.commit()
    db.refresh(novo_user)

    return _fmt_user(novo_user, db)


@router.put("/users/{user_id}")
def editar_usuario(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if payload.nome is not None:
        user.nome = payload.nome
    if payload.email is not None:
        if db.query(User).filter(User.email == payload.email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="E-mail já em uso por outro usuário")
        user.email = payload.email
    if payload.dias_totais is not None:
        user.dias_totais = payload.dias_totais
    if payload.departamento_id is not None:
        if payload.departamento_id == 0:
            user.departamento_id = None
        else:
            if not db.query(Departamento).filter(Departamento.id == payload.departamento_id).first():
                raise HTTPException(status_code=404, detail="Departamento não encontrado")
            user.departamento_id = payload.departamento_id
    if payload.data_admissao is not None:
        user.data_admissao = payload.data_admissao
    if payload.data_aniversario is not None:
        user.data_aniversario = payload.data_aniversario
    if payload.senha is not None and payload.senha.strip():
        user.senha_hash = hash_senha(payload.senha)

    log = Log(
        user_id=current_user.id,
        acao="USUARIO_EDITADO",
        detalhes=f"Usuário {user.nome} ({user.email}) editado por {current_user.nome}",
    )
    db.add(log)
    db.commit()
    db.refresh(user)

    return _fmt_user(user, db)


@router.get("/users/aniversariantes")
def listar_aniversariantes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hoje = date.today()
    aniversariantes = (
        db.query(User)
        .filter(User.data_aniversario.isnot(None))
        .order_by(User.data_aniversario)
        .all()
    )
    resultados = [
        {
            "nome": u.nome,
            "data_aniversario": u.data_aniversario,
        }
        for u in aniversariantes
        if u.data_aniversario and u.data_aniversario.month == hoje.month
    ]
    return resultados


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def excluir_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    log = Log(
        user_id=current_user.id,
        acao="USUARIO_EXCLUIDO",
        detalhes=f"Usuário {user.nome} ({user.email}) excluído por {current_user.nome}",
    )
    db.add(log)
    db.delete(user)
    db.commit()

    return {"detail": "Usuário excluído com sucesso"}


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
            raise HTTPException(status_code=400, detail="E-mail já em uso por outro usuário")
        current_user.email = payload.email

    if payload.nova_senha is not None and payload.nova_senha.strip():
        if not payload.senha_atual:
            raise HTTPException(status_code=400, detail="Informe a senha atual para alterá-la")
        if not verificar_senha(payload.senha_atual, current_user.senha_hash):
            raise HTTPException(status_code=400, detail="Senha atual incorreta")
        current_user.senha_hash = hash_senha(payload.nova_senha)

    db.commit()
    db.refresh(current_user)

    return _fmt_user(current_user, db)
