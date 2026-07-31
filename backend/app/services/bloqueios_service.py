from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.bloqueio import BloqueioData
from app.models.log import Log
from app.models.user import User
from app.repositories import bloqueios_repository
from app.schemas.bloqueio import BloqueioCreate, BloqueioUpdate

TIPOS_BLOQUEIO = ("bloqueio", "recesso")


def formatar_bloqueio(bloqueio: BloqueioData) -> dict:
    return {
        "id": bloqueio.id,
        "data_inicio": bloqueio.data_inicio,
        "data_fim": bloqueio.data_fim,
        "motivo": bloqueio.motivo,
        "tipo": bloqueio.tipo,
        "criado_por_nome": bloqueio.criado_por.nome if bloqueio.criado_por else None,
        "criado_em": bloqueio.criado_em,
    }


def validar_periodo(data_inicio, data_fim) -> None:
    if data_fim < data_inicio:
        raise HTTPException(status_code=400, detail="data_fim deve ser maior ou igual a data_inicio")


def validar_tipo(tipo: str | None) -> None:
    if tipo not in TIPOS_BLOQUEIO:
        raise HTTPException(status_code=400, detail="tipo deve ser 'bloqueio' ou 'recesso'")


def buscar_bloqueio(db: Session, bloqueio_id: int) -> BloqueioData:
    bloqueio = bloqueios_repository.obter_bloqueio_por_id(db, bloqueio_id)
    if not bloqueio:
        raise HTTPException(status_code=404, detail="Bloqueio não encontrado")
    return bloqueio


def listar_bloqueios(db: Session) -> list[dict]:
    return [formatar_bloqueio(bloqueio) for bloqueio in bloqueios_repository.listar_bloqueios(db)]


def criar_bloqueio(db: Session, payload: BloqueioCreate, current_user: User) -> dict:
    validar_periodo(payload.data_inicio, payload.data_fim)
    validar_tipo(payload.tipo)

    bloqueio = BloqueioData(
        data_inicio=payload.data_inicio,
        data_fim=payload.data_fim,
        motivo=payload.motivo,
        tipo=payload.tipo,
        criado_por_id=current_user.id,
    )
    tipo_label = "Recesso" if payload.tipo == "recesso" else "Bloqueio"
    log = Log(
        user_id=current_user.id,
        acao="BLOQUEIO_CRIADO",
        detalhes=f"{tipo_label} criado: {payload.data_inicio} a {payload.data_fim} - {payload.motivo}",
    )
    bloqueios_repository.salvar_bloqueio_com_log(db, bloqueio, log)
    return formatar_bloqueio(bloqueio)


def editar_bloqueio(db: Session, bloqueio_id: int, payload: BloqueioUpdate, current_user: User) -> dict:
    bloqueio = buscar_bloqueio(db, bloqueio_id)

    if payload.data_inicio is not None:
        bloqueio.data_inicio = payload.data_inicio
    if payload.data_fim is not None:
        bloqueio.data_fim = payload.data_fim
    if payload.motivo is not None:
        bloqueio.motivo = payload.motivo
    if payload.tipo is not None:
        validar_tipo(payload.tipo)
        bloqueio.tipo = payload.tipo

    validar_periodo(bloqueio.data_inicio, bloqueio.data_fim)

    log = Log(
        user_id=current_user.id,
        acao="BLOQUEIO_EDITADO",
        detalhes=f"Bloqueio #{bloqueio_id} atualizado: {bloqueio.data_inicio} a {bloqueio.data_fim}",
    )
    bloqueios_repository.atualizar_bloqueio_com_log(db, bloqueio, log)
    return formatar_bloqueio(bloqueio)


def excluir_bloqueio(db: Session, bloqueio_id: int, current_user: User) -> None:
    bloqueio = buscar_bloqueio(db, bloqueio_id)
    log = Log(
        user_id=current_user.id,
        acao="BLOQUEIO_EXCLUIDO",
        detalhes=f"Bloqueio #{bloqueio_id} ({bloqueio.data_inicio} a {bloqueio.data_fim}) excluido",
    )
    bloqueios_repository.excluir_bloqueio_com_log(db, bloqueio, log)
