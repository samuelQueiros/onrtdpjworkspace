from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.bloqueio import BloqueioData
from app.models.log import Log
from app.core.security import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/bloqueios", tags=["Bloqueios de Datas"])


class BloqueioCreate(BaseModel):
    data_inicio: date
    data_fim: date
    motivo: str
    tipo: Optional[str] = "bloqueio"  # "bloqueio" | "recesso"


class BloqueioUpdate(BaseModel):
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    motivo: Optional[str] = None
    tipo: Optional[str] = None


def _fmt(b: BloqueioData) -> dict:
    return {
        "id": b.id,
        "data_inicio": b.data_inicio,
        "data_fim": b.data_fim,
        "motivo": b.motivo,
        "tipo": b.tipo,
        "criado_por_nome": b.criado_por.nome if b.criado_por else None,
        "criado_em": b.criado_em,
    }


@router.get("")
def listar_bloqueios(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    bloqueios = db.query(BloqueioData).order_by(BloqueioData.data_inicio).all()
    return [_fmt(b) for b in bloqueios]


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_bloqueio(
    payload: BloqueioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if payload.data_fim < payload.data_inicio:
        raise HTTPException(status_code=400, detail="data_fim deve ser maior ou igual a data_inicio")

    if payload.tipo not in ("bloqueio", "recesso"):
        raise HTTPException(status_code=400, detail="tipo deve ser 'bloqueio' ou 'recesso'")

    bloqueio = BloqueioData(
        data_inicio=payload.data_inicio,
        data_fim=payload.data_fim,
        motivo=payload.motivo,
        tipo=payload.tipo,
        criado_por_id=current_user.id,
    )
    db.add(bloqueio)
    db.flush()

    tipo_label = "Recesso" if payload.tipo == "recesso" else "Bloqueio"
    log = Log(
        user_id=current_user.id,
        acao="BLOQUEIO_CRIADO",
        detalhes=f"{tipo_label} criado: {payload.data_inicio} a {payload.data_fim} — {payload.motivo}",
    )
    db.add(log)
    db.commit()
    db.refresh(bloqueio)
    return _fmt(bloqueio)


@router.put("/{bloqueio_id}")
def editar_bloqueio(
    bloqueio_id: int,
    payload: BloqueioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    bloqueio = db.query(BloqueioData).filter(BloqueioData.id == bloqueio_id).first()
    if not bloqueio:
        raise HTTPException(status_code=404, detail="Bloqueio não encontrado")

    if payload.data_inicio is not None:
        bloqueio.data_inicio = payload.data_inicio
    if payload.data_fim is not None:
        bloqueio.data_fim = payload.data_fim
    if payload.motivo is not None:
        bloqueio.motivo = payload.motivo
    if payload.tipo is not None:
        if payload.tipo not in ("bloqueio", "recesso"):
            raise HTTPException(status_code=400, detail="tipo deve ser 'bloqueio' ou 'recesso'")
        bloqueio.tipo = payload.tipo

    if bloqueio.data_fim < bloqueio.data_inicio:
        raise HTTPException(status_code=400, detail="data_fim deve ser maior ou igual a data_inicio")

    log = Log(
        user_id=current_user.id,
        acao="BLOQUEIO_EDITADO",
        detalhes=f"Bloqueio #{bloqueio_id} atualizado: {bloqueio.data_inicio} a {bloqueio.data_fim}",
    )
    db.add(log)
    db.commit()
    db.refresh(bloqueio)
    return _fmt(bloqueio)


@router.delete("/{bloqueio_id}", status_code=status.HTTP_200_OK)
def excluir_bloqueio(
    bloqueio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    bloqueio = db.query(BloqueioData).filter(BloqueioData.id == bloqueio_id).first()
    if not bloqueio:
        raise HTTPException(status_code=404, detail="Bloqueio não encontrado")

    log = Log(
        user_id=current_user.id,
        acao="BLOQUEIO_EXCLUIDO",
        detalhes=f"Bloqueio #{bloqueio_id} ({bloqueio.data_inicio} a {bloqueio.data_fim}) excluído",
    )
    db.add(log)
    db.delete(bloqueio)
    db.commit()
    return {"detail": "Bloqueio excluído com sucesso"}
