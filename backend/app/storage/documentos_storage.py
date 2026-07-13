import re
import unicodedata
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from fastapi import HTTPException

from app.core.config import settings
from app.models.documento import Documento
from app.models.user import User

MAX_SIZE = 10 * 1024 * 1024  # 10 MB
TIPOS_PERMITIDOS = {"application/pdf", "image/jpeg", "image/png"}
EXTENSOES_POR_MIME = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


def obter_upload_dir() -> Path:
    upload_dir = settings.upload_dir
    (upload_dir / "enviados").mkdir(parents=True, exist_ok=True)
    (upload_dir / "recebidos").mkdir(parents=True, exist_ok=True)
    return upload_dir


def inicializar_diretorios_upload() -> None:
    obter_upload_dir()


def nome_pasta_usuario(user: User) -> str:
    nome = unicodedata.normalize("NFKD", user.nome)
    nome = nome.encode("ascii", "ignore").decode("ascii").lower()
    nome = re.sub(r"[^a-z0-9]+", "-", nome).strip("-")
    return nome or "usuario"


def obter_diretorio_enviado(criado_por: User, destinatario: User) -> Path:
    diretorio = obter_upload_dir() / "enviados" / nome_pasta_usuario(criado_por) / nome_pasta_usuario(destinatario)
    diretorio.mkdir(parents=True, exist_ok=True)
    return diretorio


def obter_diretorio_recebido(destinatario: User) -> Path:
    diretorio = obter_upload_dir() / "recebidos" / nome_pasta_usuario(destinatario)
    diretorio.mkdir(parents=True, exist_ok=True)
    return diretorio


def validar_assinatura_arquivo(arquivo_bytes: bytes, mime: str) -> bool:
    if mime == "application/pdf":
        return arquivo_bytes.startswith(b"%PDF-")

    if mime == "image/jpeg":
        return arquivo_bytes.startswith(b"\xff\xd8\xff")

    if mime == "image/png":
        return arquivo_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    return False


def corrigir_nome_arquivo(nome: str | None) -> str:
    nome = Path(nome or "arquivo").name
    nome = nome.replace("\r", "").replace("\n", "").replace('"', "").replace("\\", "-").strip()
    return nome or "arquivo"


def content_disposition(tipo: str, nome_arquivo: str) -> str:
    nome_seguro = corrigir_nome_arquivo(nome_arquivo)
    nome_encoded = quote(nome_seguro)
    return f"{tipo}; filename=\"{nome_seguro}\"; filename*=UTF-8''{nome_encoded}"


def gerar_nome_armazenamento(nome_original: str | None, mime: str) -> str:
    nome_seguro = corrigir_nome_arquivo(nome_original)
    extensao = Path(nome_seguro).suffix.lower()
    if extensao not in {".pdf", ".jpg", ".jpeg", ".png"}:
        extensao = EXTENSOES_POR_MIME[mime]
    nome_base = Path(nome_seguro).stem
    nome_base = unicodedata.normalize("NFKD", nome_base)
    nome_base = nome_base.encode("ascii", "ignore").decode("ascii").lower()
    nome_base = re.sub(r"[^a-z0-9]+", "-", nome_base).strip("-")
    nome_base = nome_base or "arquivo"
    return f"{uuid4().hex}-{nome_base}{extensao}"


def caminho_documento(doc: Documento) -> Path:
    if not doc.caminho_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo do documento nao encontrado")

    upload_dir = obter_upload_dir()
    caminho = (upload_dir / doc.caminho_arquivo).resolve()

    if upload_dir not in caminho.parents and caminho != upload_dir:
        raise HTTPException(status_code=400, detail="Caminho do documento invalido")

    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="Arquivo do documento nao encontrado")

    return caminho


def caminho_documento_enviado(doc: Documento) -> Path | None:
    if not doc.caminho_enviado:
        return None

    upload_dir = obter_upload_dir()
    caminho = (upload_dir / doc.caminho_enviado).resolve()

    if upload_dir not in caminho.parents and caminho != upload_dir:
        return None

    return caminho
