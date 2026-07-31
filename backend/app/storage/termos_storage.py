import hashlib
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from app.storage.documentos_storage import obter_upload_dir


@dataclass(frozen=True, slots=True)
class TermoArquivo:
    caminho_relativo: str
    caminho_absoluto: Path
    nome_arquivo: str
    tamanho: int
    pdf_hash: str
    criado_novo: bool = False
    caminho_backup: Path | None = None


def _slug(valor: str, fallback: str, limite: int = 80) -> str:
    normalizado = unicodedata.normalize("NFKD", valor or "")
    normalizado = normalizado.encode("ascii", "ignore").decode("ascii").lower()
    normalizado = re.sub(r"[^a-z0-9]+", "-", normalizado).strip("-")
    return (normalizado or fallback)[:limite].rstrip("-")


def _validar_solicitacao_id(solicitacao_id: int) -> None:
    if not isinstance(solicitacao_id, int) or isinstance(solicitacao_id, bool) or solicitacao_id <= 0:
        raise ValueError("Identificador de solicitação inválido.")


def montar_nome_arquivo_termo(
    nome_colaborador: str,
    solicitacao_id: int,
    versao_codigo: str,
) -> str:
    _validar_solicitacao_id(solicitacao_id)
    nome = _slug(nome_colaborador, "colaborador")
    versao = _slug(versao_codigo, "versao", limite=30)
    return f"termo-equipamentos-{nome}-solicitacao-{solicitacao_id}-{versao}.pdf"


def _diretorio_termo(nome_colaborador: str, solicitacao_id: int) -> Path:
    _validar_solicitacao_id(solicitacao_id)
    upload_dir = obter_upload_dir().resolve()
    diretorio = (
        upload_dir
        / "termos-equipamentos"
        / _slug(nome_colaborador, "colaborador")
        / f"solicitacao-{solicitacao_id}"
    ).resolve()
    if upload_dir not in diretorio.parents:
        raise ValueError("Caminho de armazenamento do termo inválido.")
    diretorio.mkdir(parents=True, exist_ok=True)
    return diretorio


def _hash_arquivo(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _resultado(
    caminho: Path,
    pdf_hash: str,
    criado_novo: bool = False,
    caminho_backup: Path | None = None,
) -> TermoArquivo:
    upload_dir = obter_upload_dir().resolve()
    caminho_resolvido = caminho.resolve()
    if upload_dir not in caminho_resolvido.parents:
        raise ValueError("Caminho do termo fora do diretório de uploads.")
    return TermoArquivo(
        caminho_relativo=caminho_resolvido.relative_to(upload_dir).as_posix(),
        caminho_absoluto=caminho_resolvido,
        nome_arquivo=caminho_resolvido.name,
        tamanho=caminho_resolvido.stat().st_size,
        pdf_hash=pdf_hash,
        criado_novo=criado_novo,
        caminho_backup=caminho_backup,
    )


def salvar_termo_pdf(
    pdf_bytes: bytes,
    nome_colaborador: str,
    solicitacao_id: int,
    versao_codigo: str,
) -> TermoArquivo:
    """Salva o termo em arquivo único por solicitação/versão usando troca atômica."""
    if not isinstance(pdf_bytes, bytes) or not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Conteúdo do termo não é um PDF válido.")

    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
    diretorio = _diretorio_termo(nome_colaborador, solicitacao_id)
    nome_arquivo = montar_nome_arquivo_termo(nome_colaborador, solicitacao_id, versao_codigo)
    destino = diretorio / nome_arquivo

    # Chamadas repetidas com o mesmo conteúdo não reescrevem o artefato.
    destino_existia = destino.is_file()
    if destino_existia and _hash_arquivo(destino) == pdf_hash:
        return _resultado(destino, pdf_hash)

    temporario: Path | None = None
    backup: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=diretorio,
            prefix=f".{nome_arquivo}.",
            suffix=".tmp",
            delete=False,
        ) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(pdf_bytes)
            arquivo.flush()
            os.fsync(arquivo.fileno())

        if destino_existia:
            with tempfile.NamedTemporaryFile(
                dir=diretorio,
                prefix=f".{nome_arquivo}.",
                suffix=".bak",
                delete=False,
            ) as arquivo_backup:
                backup = Path(arquivo_backup.name)
            os.replace(destino, backup)
        os.replace(temporario, destino)
        temporario = None
        return _resultado(
            destino,
            pdf_hash,
            criado_novo=not destino_existia,
            caminho_backup=backup,
        )
    except Exception:
        if backup is not None and backup.exists():
            destino.unlink(missing_ok=True)
            os.replace(backup, destino)
            backup = None
        raise
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)


def confirmar_termo_pdf(arquivo: TermoArquivo) -> None:
    if arquivo.caminho_backup is not None:
        try:
            arquivo.caminho_backup.unlink(missing_ok=True)
        except OSError:
            # O artefato definitivo ja foi persistido. Um backup residual pode
            # ser removido posteriormente sem invalidar o documento confirmado.
            pass


def reverter_termo_pdf(arquivo: TermoArquivo) -> None:
    if arquivo.caminho_backup is not None and arquivo.caminho_backup.exists():
        arquivo.caminho_absoluto.unlink(missing_ok=True)
        os.replace(arquivo.caminho_backup, arquivo.caminho_absoluto)
    elif arquivo.criado_novo:
        arquivo.caminho_absoluto.unlink(missing_ok=True)
