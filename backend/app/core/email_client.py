"""Wrapper fino de protocolo SMTP/IMAP para a conta Gmail dedicada ao envio de lembretes
de ferias. Sem regra de negocio aqui - so transporte. Nunca logar senha ou corpo de e-mail.

Sempre TLS: `smtplib.SMTP_SSL` (465) e `imaplib.IMAP4_SSL` (993).
"""

from __future__ import annotations

import imaplib
import logging
import smtplib
from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from typing import Iterator, Literal

from app.core.config import settings

logger = logging.getLogger("app.email")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
CONEXAO_TIMEOUT_SEGUNDOS = 30

CODIGOS_BOUNCE_TEMPORARIOS = {"421", "450", "451", "452"}
CODIGOS_BOUNCE_DEFINITIVOS = {"550", "551", "552", "553", "554"}

MENSAGENS_BOUNCE_AMIGAVEIS: dict[str, str] = {
    "421": "Servidor do destinatário temporariamente indisponível.",
    "450": "Caixa de e-mail do destinatário temporariamente indisponível.",
    "451": "Erro temporário no processamento pelo servidor de e-mail.",
    "452": "Sistema do destinatário sem espaço/recursos no momento.",
    "550": "Endereço de e-mail do destinatário não existe ou foi rejeitado.",
    "551": "Usuário não está mais nesse servidor.",
    "552": "Caixa de e-mail do destinatário está cheia.",
    "553": "Endereço de e-mail do destinatário é inválido.",
    "554": "Transação rejeitada pelo servidor do destinatário.",
}


class EmailEnvioError(Exception):
    """Erro de autenticação/conexão ao falar com o Gmail - nunca deve vazar traceback cru
    para o cliente HTTP."""


def enviar_email_smtp(destinatario: str, assunto: str, texto_plain: str, texto_html: str) -> str:
    """Envia um e-mail multipart/alternative (texto puro + HTML) e retorna o Message-ID usado.

    Levanta `EmailEnvioError` (mensagem já traduzida) em qualquer falha de autenticação/conexão.
    Não trata bounce aqui - bounce chega depois, assíncrono, via IMAP.
    """
    if not settings.gmail_user or not settings.gmail_app_password:
        raise EmailEnvioError("Credenciais de e-mail não configuradas no servidor.")

    message_id = make_msgid()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = settings.gmail_user
    msg["To"] = destinatario
    msg["Message-ID"] = message_id
    msg.attach(MIMEText(texto_plain, "plain", "utf-8"))
    msg.attach(MIMEText(texto_html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=CONEXAO_TIMEOUT_SEGUNDOS) as smtp:
            smtp.login(settings.gmail_user, settings.gmail_app_password)
            smtp.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("falha ao enviar e-mail via smtp: %s", type(exc).__name__)
        raise EmailEnvioError("Não foi possível enviar o e-mail. Verifique a conexão/credenciais.") from exc

    logger.info("email enviado message_id=%s", message_id)
    return message_id


@contextmanager
def conectar_imap() -> Iterator[imaplib.IMAP4_SSL]:
    """Context manager de uma conexão IMAP autenticada, somente leitura (`readonly=True`
    no SELECT) - reforço extra contra qualquer STORE/EXPUNGE acidental. Fecha a conexão
    sempre, mesmo em caso de erro."""
    if not settings.gmail_user or not settings.gmail_app_password:
        raise EmailEnvioError("Credenciais de e-mail não configuradas no servidor.")

    imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=CONEXAO_TIMEOUT_SEGUNDOS)
    try:
        imap.login(settings.gmail_user, settings.gmail_app_password)
        imap.select("INBOX", readonly=True)
        yield imap
    except (imaplib.IMAP4.error, OSError) as exc:
        logger.error("falha ao conectar/autenticar no imap: %s", type(exc).__name__)
        raise EmailEnvioError("Não foi possível conectar à caixa de entrada.") from exc
    finally:
        try:
            imap.logout()
        except Exception:  # noqa: BLE001 - encerramento best-effort, nunca deve derrubar o ciclo
            pass


def classificar_codigo_bounce(codigo: str | None) -> Literal["temporario", "definitivo"] | None:
    if not codigo:
        return None
    if codigo in CODIGOS_BOUNCE_TEMPORARIOS or codigo.startswith("4"):
        return "temporario"
    if codigo in CODIGOS_BOUNCE_DEFINITIVOS or codigo.startswith("5"):
        return "definitivo"
    return None
