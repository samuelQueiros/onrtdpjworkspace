from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.aviso import Aviso
from app.models.user import User
from app.models.log import Log
from app.schemas.aviso import AvisoCreate, AvisoUpdate
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/avisos", tags=["Mural de Avisos"])


def _fmt(aviso: Aviso) -> dict:
    return {
        "id": aviso.id,
        "titulo": aviso.titulo,
        "conteudo": aviso.conteudo,
        "fixado": aviso.fixado,
        "data_expiracao": aviso.data_expiracao,
        "criado_por_nome": aviso.criado_por.nome if aviso.criado_por else "Sistema",
        "criado_em": aviso.criado_em,
    }


@router.get("")
def listar_avisos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    hoje = date.today()
    avisos = (
        db.query(Aviso)
        .filter(
            (Aviso.data_expiracao == None) | (Aviso.data_expiracao >= hoje)  # noqa: E711
        )
        .order_by(Aviso.fixado.desc(), Aviso.criado_em.desc())
        .all()
    )
    return [_fmt(a) for a in avisos]


@router.get("/todos")
def listar_todos_avisos(db: Session = Depends(get_db), _=Depends(require_admin)):
    avisos = db.query(Aviso).order_by(Aviso.fixado.desc(), Aviso.criado_em.desc()).all()
    return [_fmt(a) for a in avisos]


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_aviso(
    payload: AvisoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    aviso = Aviso(
        titulo=payload.titulo,
        conteudo=payload.conteudo,
        fixado=payload.fixado,
        data_expiracao=payload.data_expiracao,
        criado_por_id=current_user.id,
    )
    db.add(aviso)
    db.flush()

    log = Log(
        user_id=current_user.id,
        acao="AVISO_CRIADO",
        detalhes=f"Aviso '{aviso.titulo}' publicado",
    )
    db.add(log)
    db.commit()
    db.refresh(aviso)

    return _fmt(aviso)


@router.put("/{aviso_id}")
def editar_aviso(
    aviso_id: int,
    payload: AvisoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    aviso = db.query(Aviso).filter(Aviso.id == aviso_id).first()
    if not aviso:
        raise HTTPException(status_code=404, detail="Aviso não encontrado")

    if payload.titulo is not None:
        aviso.titulo = payload.titulo
    if payload.conteudo is not None:
        aviso.conteudo = payload.conteudo
    if payload.fixado is not None:
        aviso.fixado = payload.fixado
    if payload.data_expiracao is not None:
        aviso.data_expiracao = payload.data_expiracao

    log = Log(
        user_id=current_user.id,
        acao="AVISO_EDITADO",
        detalhes=f"Aviso #{aviso_id} atualizado",
    )
    db.add(log)
    db.commit()
    db.refresh(aviso)

    return _fmt(aviso)


@router.delete("/{aviso_id}", status_code=status.HTTP_200_OK)
def excluir_aviso(
    aviso_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    aviso = db.query(Aviso).filter(Aviso.id == aviso_id).first()
    if not aviso:
        raise HTTPException(status_code=404, detail="Aviso não encontrado")

    log = Log(
        user_id=current_user.id,
        acao="AVISO_EXCLUIDO",
        detalhes=f"Aviso '{aviso.titulo}' excluído",
    )
    db.add(log)
    db.delete(aviso)
    db.commit()

    return {"detail": "Aviso excluído com sucesso"}
