"""Job periódico (chamado pelo APScheduler, ver app/core/scheduler.py) que avança a state
machine de cada `Envio` em status `monitorando`: prazo estourado, resposta do destinatário
ou bounce (temporário/definitivo). Roda sem `current_user` (ação do sistema) - por isso os
eventos gravados aqui têm `criado_por_id=None`, diferente das transições disparadas por um
admin.
"""

import email
import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core import email_client, email_parsing
from app.core.timezone import FUSO_SAO_PAULO
from app.models.envio import Envio, EnvioEvento
from app.repositories import envios_repository

logger = logging.getLogger("app.envios_monitoramento")

LOCK_KEY_MONITORAMENTO = 4_000_001


def executar_ciclo_monitoramento(db: Session) -> None:
    """Ponto de entrada do job. Usa `pg_try_advisory_lock` (não-bloqueante) para pular o
    ciclo inteiro se outro já estiver em andamento - diferente de `sincronizar_alertas`/
    `bloquear_regras_ferias`, que usam locks transacionais para *esperar* a vez, este job
    quer *desistir* se já tem um rodando (não faz sentido enfileirar polls de 15-30min)."""
    dialect = getattr(getattr(db, "bind", None), "dialect", None)
    usa_postgres = getattr(dialect, "name", None) == "postgresql"

    if usa_postgres:
        obtido = db.execute(
            text("SELECT pg_try_advisory_lock(:chave)"), {"chave": LOCK_KEY_MONITORAMENTO}
        ).scalar()
        if not obtido:
            return

    try:
        _processar_ciclo(db)
    finally:
        if usa_postgres:
            db.execute(text("SELECT pg_advisory_unlock(:chave)"), {"chave": LOCK_KEY_MONITORAMENTO})
            db.commit()


def _processar_ciclo(db: Session) -> None:
    pendentes = envios_repository.listar_envios_monitorando(db)
    if not pendentes:
        return

    agora = datetime.now(FUSO_SAO_PAULO)
    vencidos = [envio for envio in pendentes if agora >= envio.prazo_limite]
    ativos = [envio for envio in pendentes if envio not in vencidos]

    # Prazo vencido é checado primeiro e não precisa nem tocar o IMAP nesse ciclo.
    for envio in vencidos:
        _marcar_sem_retorno(db, envio, agora)

    if not ativos:
        return

    try:
        with email_client.conectar_imap() as imap:
            mensagens = _buscar_mensagens_recentes(imap, ativos)
    except email_client.EmailEnvioError:
        logger.exception("falha ao conectar ao imap durante o ciclo de monitoramento")
        return

    for envio in ativos:
        try:
            _processar_envio(db, envio, mensagens, agora)
        except Exception:
            logger.exception("falha ao processar envio #%s no ciclo de monitoramento", envio.id)
            db.rollback()
            envio.ultima_verificacao_em = agora
            _registrar_evento(db, envio, tipo="erro_verificacao", detalhes="Falha ao processar verificação.")
            db.commit()


def _buscar_mensagens_recentes(imap, envios: list[Envio]) -> list[email.message.Message]:
    """Uma única busca IMAP por ciclo (não uma por envio) - critério `SINCE` limita o
    escopo, nunca varre a caixa inteira. As mensagens retornadas são casadas localmente
    (em Python) contra o `message_id` de cada envio ativo."""
    data_mais_antiga = min(envio.enviado_em for envio in envios)
    criterio = data_mais_antiga.strftime("%d-%b-%Y")
    typ, dados = imap.search(None, f'(SINCE "{criterio}")')
    if typ != "OK" or not dados or not dados[0]:
        return []

    mensagens = []
    for numero in dados[0].split():
        typ, resposta = imap.fetch(numero, "(RFC822)")
        if typ != "OK" or not resposta or not resposta[0]:
            continue
        bruto = resposta[0][1]
        mensagens.append(email.message_from_bytes(bruto))
    return mensagens


def _processar_envio(db: Session, envio: Envio, mensagens: list, agora: datetime) -> None:
    resposta = None
    bounce = None
    for mensagem in mensagens:
        referencias = " ".join(
            filtro for filtro in (mensagem.get("In-Reply-To"), mensagem.get("References")) if filtro
        )
        if envio.message_id not in referencias:
            continue
        remetente = (mensagem.get("From") or "").lower()
        if "mailer-daemon" in remetente or "postmaster" in remetente:
            bounce = mensagem
        else:
            resposta = mensagem
            break

    if resposta is not None:
        _marcar_respondido(db, envio, resposta, agora)
        return

    if bounce is not None:
        info = email_parsing.interpretar_bounce(bounce)
        referenciado = (info or {}).get("message_id_referenciado") or ""
        if info and envio.message_id in referenciado:
            _classificar_bounce(db, envio, info["codigo"], agora)
            return

    envio.ultima_verificacao_em = agora
    db.commit()


def _registrar_evento(
    db: Session,
    envio: Envio,
    *,
    tipo: str,
    detalhes: str | None = None,
    status_anterior: str | None = None,
    status_novo: str | None = None,
) -> None:
    db.add(
        EnvioEvento(
            envio=envio,
            tipo=tipo,
            status_anterior=status_anterior,
            status_novo=status_novo,
            detalhes=detalhes,
            criado_por_id=None,
        )
    )


def _marcar_sem_retorno(db: Session, envio: Envio, agora: datetime) -> None:
    envio.status = "sem_retorno"
    envio.ultima_verificacao_em = agora
    _registrar_evento(db, envio, tipo="prazo_estourado", status_anterior="monitorando", status_novo="sem_retorno")
    db.commit()


def _marcar_respondido(db: Session, envio: Envio, mensagem, agora: datetime) -> None:
    resposta_texto, resposta_bruta = email_parsing.preparar_resposta(mensagem)
    envio.status = "respondido"
    envio.resposta_texto = resposta_texto
    envio.resposta_bruta = resposta_bruta
    envio.respondido_em = agora
    envio.ultima_verificacao_em = agora
    _registrar_evento(db, envio, tipo="resposta_detectada", status_anterior="monitorando", status_novo="respondido")
    db.commit()


def _classificar_bounce(db: Session, envio: Envio, codigo: str, agora: datetime) -> None:
    classificacao = email_client.classificar_codigo_bounce(codigo)

    if classificacao == "definitivo":
        envio.status = "erro_definitivo"
        envio.erro_codigo = codigo
        envio.erro_mensagem = email_client.MENSAGENS_BOUNCE_AMIGAVEIS.get(
            codigo, "Falha permanente na entrega do e-mail."
        )
        envio.ultima_verificacao_em = agora
        _registrar_evento(
            db,
            envio,
            tipo="bounce_definitivo",
            status_anterior="monitorando",
            status_novo="erro_definitivo",
            detalhes=f"Código SMTP {codigo}",
        )
    elif classificacao == "temporario":
        envio.tentativas_verificacao += 1
        envio.ultima_verificacao_em = agora
        _registrar_evento(
            db,
            envio,
            tipo="bounce_temporario",
            detalhes=f"Código SMTP {codigo} (tentativa {envio.tentativas_verificacao})",
        )
    else:
        envio.ultima_verificacao_em = agora

    db.commit()
