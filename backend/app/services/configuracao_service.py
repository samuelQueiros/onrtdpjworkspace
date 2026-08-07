from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.configuracao import Configuracao
from app.models.user import User
from app.repositories import configuracao_repository
from app.schemas.configuracao import ConfiguracaoUpdate
from app.services import log_service


def formatar_configuracao(configuracao: Configuracao) -> dict:
    return {
        "email_destinatario": configuracao.email_destinatario,
        "atualizado_em": configuracao.atualizado_em,
    }


def obter_configuracao(db: Session) -> Configuracao:
    configuracao = configuracao_repository.obter_configuracao(db)
    if not configuracao:
        raise HTTPException(
            status_code=404,
            detail="E-mail de destino dos lembretes de férias ainda não foi configurado.",
        )
    return configuracao


def atualizar_configuracao(db: Session, payload: ConfiguracaoUpdate, current_user: User) -> dict:
    configuracao = configuracao_repository.obter_configuracao(db) or Configuracao(id=1)
    configuracao.email_destinatario = payload.email_destinatario

    log = log_service.construir_log(
        current_user,
        acao="CONFIGURACAO_EMAIL_ATUALIZADA",
        detalhes=f"E-mail de destino dos lembretes de férias atualizado para {payload.email_destinatario}",
    )
    configuracao_repository.salvar_configuracao_com_log(db, configuracao, log)
    return formatar_configuracao(configuracao)
