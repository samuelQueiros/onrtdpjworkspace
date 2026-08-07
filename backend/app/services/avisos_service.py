from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.timezone import hoje_sao_paulo
from app.models.aviso import Aviso
from app.models.user import User
from app.repositories import avisos_repository
from app.schemas.aviso import AvisoCreate, AvisoUpdate
from app.services import log_service


def formatar_aviso(aviso: Aviso) -> dict:
    return {
        "id": aviso.id,
        "titulo": aviso.titulo,
        "conteudo": aviso.conteudo,
        "fixado": aviso.fixado,
        "data_expiracao": aviso.data_expiracao,
        "criado_por_nome": aviso.criado_por.nome if aviso.criado_por else "Sistema",
        "criado_em": aviso.criado_em,
    }


def buscar_aviso(db: Session, aviso_id: int) -> Aviso:
    aviso = avisos_repository.obter_aviso_por_id(db, aviso_id)
    if not aviso:
        raise HTTPException(status_code=404, detail="Aviso não encontrado")
    return aviso


def listar_avisos(db: Session) -> list[dict]:
    return [formatar_aviso(aviso) for aviso in avisos_repository.listar_avisos_ativos(db, hoje_sao_paulo())]


def listar_todos_avisos(db: Session) -> list[dict]:
    return [formatar_aviso(aviso) for aviso in avisos_repository.listar_todos_avisos(db)]


def criar_aviso(db: Session, payload: AvisoCreate, current_user: User) -> dict:
    aviso = Aviso(
        titulo=payload.titulo,
        conteudo=payload.conteudo,
        fixado=payload.fixado,
        data_expiracao=payload.data_expiracao,
        criado_por_id=current_user.id,
    )
    log = log_service.construir_log(
        current_user,
        acao="AVISO_CRIADO",
        detalhes=f"Aviso '{aviso.titulo}' publicado",
    )
    avisos_repository.salvar_aviso_com_log(db, aviso, log)
    return formatar_aviso(aviso)


def editar_aviso(db: Session, aviso_id: int, payload: AvisoUpdate, current_user: User) -> dict:
    aviso = buscar_aviso(db, aviso_id)

    if payload.titulo is not None:
        aviso.titulo = payload.titulo
    if payload.conteudo is not None:
        aviso.conteudo = payload.conteudo
    if payload.fixado is not None:
        aviso.fixado = payload.fixado
    if payload.data_expiracao is not None:
        aviso.data_expiracao = payload.data_expiracao

    log = log_service.construir_log(
        current_user,
        acao="AVISO_EDITADO",
        detalhes=f"Aviso #{aviso_id} atualizado",
    )
    avisos_repository.atualizar_aviso_com_log(db, aviso, log)
    return formatar_aviso(aviso)


def excluir_aviso(db: Session, aviso_id: int, current_user: User) -> None:
    aviso = buscar_aviso(db, aviso_id)
    log = log_service.construir_log(
        current_user,
        acao="AVISO_EXCLUIDO",
        detalhes=f"Aviso '{aviso.titulo}' excluído",
    )
    avisos_repository.excluir_aviso_com_log(db, aviso, log)
