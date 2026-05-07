from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.departamento import Departamento
from app.models.user import User
from app.models.log import Log
from app.schemas.departamento import DepartamentoCreate, DepartamentoUpdate
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


@router.get("")
def listar_departamentos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    deps = db.query(Departamento).order_by(Departamento.nome).all()
    return [
        {
            "id": d.id,
            "nome": d.nome,
            "limite_simultaneo": d.limite_simultaneo,
            "total_usuarios": db.query(User).filter(User.departamento_id == d.id).count(),
            "criado_em": d.criado_em,
        }
        for d in deps
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_departamento(
    payload: DepartamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(Departamento).filter(Departamento.nome == payload.nome).first():
        raise HTTPException(status_code=400, detail="Já existe um departamento com esse nome")

    dep = Departamento(nome=payload.nome, limite_simultaneo=payload.limite_simultaneo)
    db.add(dep)
    db.flush()

    log = Log(
        user_id=current_user.id,
        acao="DEPARTAMENTO_CRIADO",
        detalhes=f"Departamento '{dep.nome}' criado (limite: {dep.limite_simultaneo})",
    )
    db.add(log)
    db.commit()
    db.refresh(dep)

    return {"id": dep.id, "nome": dep.nome, "limite_simultaneo": dep.limite_simultaneo, "criado_em": dep.criado_em}


@router.put("/{dep_id}")
def editar_departamento(
    dep_id: int,
    payload: DepartamentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    dep = db.query(Departamento).filter(Departamento.id == dep_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    if payload.nome is not None:
        existente = db.query(Departamento).filter(
            Departamento.nome == payload.nome, Departamento.id != dep_id
        ).first()
        if existente:
            raise HTTPException(status_code=400, detail="Já existe um departamento com esse nome")
        dep.nome = payload.nome

    if payload.limite_simultaneo is not None:
        dep.limite_simultaneo = payload.limite_simultaneo

    log = Log(
        user_id=current_user.id,
        acao="DEPARTAMENTO_EDITADO",
        detalhes=f"Departamento #{dep_id} atualizado",
    )
    db.add(log)
    db.commit()
    db.refresh(dep)

    return {"id": dep.id, "nome": dep.nome, "limite_simultaneo": dep.limite_simultaneo, "criado_em": dep.criado_em}


@router.delete("/{dep_id}", status_code=status.HTTP_200_OK)
def excluir_departamento(
    dep_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    dep = db.query(Departamento).filter(Departamento.id == dep_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    # Desvincular usuários antes de excluir
    db.query(User).filter(User.departamento_id == dep_id).update({"departamento_id": None})

    log = Log(
        user_id=current_user.id,
        acao="DEPARTAMENTO_EXCLUIDO",
        detalhes=f"Departamento '{dep.nome}' excluído",
    )
    db.add(log)
    db.delete(dep)
    db.commit()

    return {"detail": "Departamento excluído com sucesso"}
