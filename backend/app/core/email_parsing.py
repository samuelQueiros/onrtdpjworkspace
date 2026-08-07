"""Parsing de mensagens de e-mail (resposta e bounce). Sem I/O de rede - so processamento
de texto puro, testavel sem mockar socket nenhum.

A remocao de citacao e best-effort (nao precisa ser perfeita): `resposta_bruta` sempre fica
disponivel como fallback caso a extracao/corte falhe ou fique incompleta.
"""

from __future__ import annotations

import html
import re
from email.message import Message

RESPOSTA_TEXTO_MAX_CHARS = 5000
RESPOSTA_BRUTA_MAX_CHARS = 20000

_PADRAO_CITACAO = re.compile(
    r"^(em .+ escreveu:|on .+ wrote:|-{2,}\s*(mensagem original|original message)\s*-{2,}.*|>.*)$",
    re.IGNORECASE,
)
_PADRAO_CABECALHO_DE = re.compile(r"^(de|from):\s", re.IGNORECASE)
_PADRAO_CABECALHOS_SEGUINTES = re.compile(
    r"^(enviado|sent|para|to|assunto|subject):\s", re.IGNORECASE
)
_PADRAO_CODIGO_SMTP = re.compile(r"\b([45]\d{2})\b")


def _remover_controle(texto: str) -> str:
    return "".join(ch for ch in texto if ch in "\n\t" or ch >= " ")


def extrair_texto_puro(msg: Message) -> str:
    """Extrai a parte text/plain de uma mensagem; cai para um strip cru de tags se só
    houver text/html (aceitável pois o resultado nunca é renderizado como HTML)."""
    if msg.is_multipart():
        for parte in msg.walk():
            disposicao = parte.get("Content-Disposition", "")
            if parte.get_content_type() == "text/plain" and not disposicao.startswith("attachment"):
                texto = _decodificar_parte(parte)
                if texto is not None:
                    return texto
        for parte in msg.walk():
            if parte.get_content_type() == "text/html":
                bruto_html = _decodificar_parte(parte)
                if bruto_html is not None:
                    return html.unescape(re.sub(r"<[^>]+>", " ", bruto_html))
        return ""

    if msg.get_content_type() == "text/html":
        bruto_html = _decodificar_parte(msg)
        if bruto_html is not None:
            return html.unescape(re.sub(r"<[^>]+>", " ", bruto_html))

    return _decodificar_parte(msg) or ""


def _decodificar_parte(parte: Message) -> str | None:
    payload = parte.get_payload(decode=True)
    if not payload:
        return None
    charset = parte.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def remover_citacao(texto: str) -> str:
    """Corta o texto no primeiro sinal de citação do e-mail original: 'Em ... escreveu:'
    (Gmail pt-BR), 'On ... wrote:' (Gmail en), bloco De/Enviado/Para/Assunto (Outlook) ou
    linha iniciada com '>'."""
    linhas = texto.splitlines()
    resultado: list[str] = []
    for indice, linha in enumerate(linhas):
        linha_strip = linha.strip()
        if _PADRAO_CITACAO.match(linha_strip):
            break
        se_bloco_outlook = _PADRAO_CABECALHO_DE.match(linha_strip) and any(
            _PADRAO_CABECALHOS_SEGUINTES.match(seguinte.strip())
            for seguinte in linhas[indice + 1 : indice + 4]
        )
        if se_bloco_outlook:
            break
        resultado.append(linha)
    return "\n".join(resultado).strip()


def preparar_resposta(msg: Message) -> tuple[str, str]:
    """Retorna (resposta_texto, resposta_bruta) já limpos de caracteres de controle e
    truncados como defesa contra corpo malicioso/gigante."""
    bruto = _remover_controle(extrair_texto_puro(msg))
    limpo = _remover_controle(remover_citacao(bruto))
    return limpo[:RESPOSTA_TEXTO_MAX_CHARS], bruto[:RESPOSTA_BRUTA_MAX_CHARS]


def interpretar_bounce(msg: Message) -> dict | None:
    """Extrai o código SMTP e o Message-ID original referenciado de uma DSN (Delivery
    Status Notification). Retorna None se a mensagem não parecer uma DSN válida - a
    validação de origem (remetente + Message-ID batendo com o envio esperado) é feita
    por quem chama esta função, não aqui."""
    message_id_referenciado = msg.get("References") or msg.get("In-Reply-To")
    codigo = None

    partes = list(msg.walk()) if msg.is_multipart() else [msg]
    for parte in partes:
        if parte.get_content_type() not in ("message/delivery-status", "text/plain"):
            continue
        texto = _decodificar_parte(parte)
        if not texto:
            continue
        match = _PADRAO_CODIGO_SMTP.search(texto)
        if match:
            codigo = match.group(1)
            break

    if not codigo:
        return None
    return {"codigo": codigo, "message_id_referenciado": message_id_referenciado}
