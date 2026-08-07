import html
import re
import secrets
from datetime import datetime, time

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import email_client
from app.core.config import settings
from app.core.timezone import FUSO_SAO_PAULO, hoje_sao_paulo
from app.models.envio import Envio, EnvioEvento
from app.models.user import User
from app.repositories import alertas_repository, envios_repository
from app.services import alertas_service, configuracao_service, ferias_service, log_service

_PADRAO_NEGRITO = re.compile(r"\*\*(.+?)\*\*")


def _texto_para_html(texto: str) -> str:
    escapado = html.escape(texto)
    com_negrito = _PADRAO_NEGRITO.sub(r"<strong>\1</strong>", escapado)
    return com_negrito.replace("\n", "<br>\n")


def montar_email_ferias(alerta: dict, token: str) -> tuple[str, str, str]:
    """Monta (assunto, texto_plain, texto_html) para o e-mail de aviso de férias.

    Reaproveita `alertas_service.gerar_texto_email` para o conteúdo (não duplica a lógica
    de texto), mas é a ÚNICA função que injeta o pixel de rastreio - e só na parte HTML,
    já que um corpo `text/plain` nunca renderiza uma tag `<img>`. Função isolada de
    propósito único: não deve ser reaproveitada por nenhum outro tipo de e-mail futuro.
    """
    texto_plain = alertas_service.gerar_texto_email(alerta)
    nome = alerta.get("ferias_usuario") or "Colaborador"
    assunto = f"Aviso de férias - {nome}"

    # /api/ é o prefixo que o nginx do frontend faz proxy para o backend (removendo o
    # prefixo antes de repassar) - a URL pública precisa passar por ele, o backend nunca
    # é alcançável diretamente da internet.
    pixel_url = f"{settings.public_app_url}/api/track/{token}.png"
    texto_html = (
        "<html><body>"
        f"<p>{_texto_para_html(texto_plain)}</p>"
        f'<img src="{pixel_url}" width="1" height="1" style="display:none" alt="">'
        "</body></html>"
    )
    return assunto, texto_plain, texto_html


def _periodo_ferias_snapshot(alerta: dict) -> str:
    data_inicio = alerta.get("ferias_data_inicio")
    data_fim = alerta.get("ferias_data_fim")
    if not data_inicio or not data_fim:
        return ""
    return f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"


def enviar_lembrete(db: Session, alerta_id: int, current_user: User) -> dict:
    alerta = alertas_repository.obter_alerta_por_id(db, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Aviso de férias não encontrado.")

    if envios_repository.obter_envio_por_alerta_id(db, alerta_id):
        raise HTTPException(status_code=409, detail="Já existe um envio registrado para este aviso.")

    alerta_dict = alertas_service.formatar_alerta(alerta, db)
    configuracao = configuracao_service.obter_configuracao(db)

    token = secrets.token_urlsafe(32)
    assunto, texto_plain, texto_html = montar_email_ferias(alerta_dict, token)

    # Fora de qualquer transação de escrita: se o Gmail recusar a autenticação/conexão,
    # nenhuma linha deve ser criada - nada foi de fato enviado.
    try:
        message_id = email_client.enviar_email_smtp(
            configuracao.email_destinatario, assunto, texto_plain, texto_html
        )
    except email_client.EmailEnvioError:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível enviar o e-mail. Tente novamente em instantes.",
        )

    enviado_em = datetime.now(FUSO_SAO_PAULO)
    prazo_limite = datetime.combine(
        ferias_service.calcular_dias_uteis(hoje_sao_paulo(), 2),
        time(23, 59, 59),
        tzinfo=FUSO_SAO_PAULO,
    )

    envio = Envio(
        alerta_id=alerta_id,
        colaborador_nome_snapshot=alerta_dict.get("ferias_usuario") or "Colaborador",
        periodo_ferias_snapshot=_periodo_ferias_snapshot(alerta_dict),
        destinatario_email_snapshot=configuracao.email_destinatario,
        message_id=message_id,
        token_rastreio=token,
        # ENVIADO -> MONITORANDO já acontece nesta mesma request (aceito pelo Gmail =
        # pronto para monitoramento); o evento "envio_criado" preserva o marco histórico.
        status="monitorando",
        enviado_em=enviado_em,
        prazo_limite=prazo_limite,
        enviado_por_id=current_user.id,
    )
    evento = EnvioEvento(
        envio=envio,
        tipo="envio_criado",
        status_novo="monitorando",
        criado_por_id=current_user.id,
    )
    log = log_service.construir_log(
        current_user,
        acao="LEMBRETE_FERIAS_ENVIADO",
        detalhes=f"Lembrete de férias enviado para {configuracao.email_destinatario} (aviso #{alerta_id}).",
    )

    envios_repository.salvar(db, envio, evento, log)
    try:
        envios_repository.commit(db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um envio registrado para este aviso.")

    return formatar_envio(envio)


def formatar_envio(envio: Envio) -> dict:
    return {
        "id": envio.id,
        "alerta_id": envio.alerta_id,
        "colaborador_nome_snapshot": envio.colaborador_nome_snapshot,
        "periodo_ferias_snapshot": envio.periodo_ferias_snapshot,
        "destinatario_email_snapshot": envio.destinatario_email_snapshot,
        "status": envio.status,
        "erro_codigo": envio.erro_codigo,
        "erro_mensagem": envio.erro_mensagem,
        "tentativas_verificacao": envio.tentativas_verificacao,
        "enviado_em": envio.enviado_em,
        "prazo_limite": envio.prazo_limite,
        "ultima_verificacao_em": envio.ultima_verificacao_em,
        "lido_em": envio.lido_em,
        "respondido_em": envio.respondido_em,
        "resposta_texto": envio.resposta_texto,
        "eventos": [
            {
                "id": evento.id,
                "tipo": evento.tipo,
                "status_anterior": evento.status_anterior,
                "status_novo": evento.status_novo,
                "detalhes": evento.detalhes,
                "criado_em": evento.criado_em,
            }
            for evento in envio.eventos
        ],
    }


def listar_envios(db: Session) -> list[dict]:
    return [formatar_envio(envio) for envio in envios_repository.listar_envios(db)]
