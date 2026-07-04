import os
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.documento import Documento
from app.models.log import Log
from app.models.user import User

router = APIRouter(prefix="/documentos", tags=["Documentos"])

MAX_SIZE = 10 * 1024 * 1024  # 10 MB
TIPOS_PERMITIDOS = {"application/pdf", "image/jpeg", "image/png"}
EXTENSOES_POR_MIME = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


def obter_upload_dir() -> Path:
    upload_dir = Path(os.getenv("UPLOAD_DIR", "data/uploads")).resolve()
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


def _fmt(doc: Documento) -> dict:
    return {
        "id": doc.id,
        "user_id": doc.user_id,
        "tipo": doc.tipo,
        "nome_arquivo": doc.nome_arquivo,
        "mime_type": doc.mime_type,
        "tamanho": doc.tamanho,
        "criado_por_nome": doc.criado_por.nome if doc.criado_por else "Sistema",
        "criado_em": doc.criado_em,
    }


def corrigir_nome_arquivo(nome: str | None) -> str:
    nome = Path(nome or "arquivo").name
    nome = nome.replace("\r", "").replace("\n", "").strip()
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


def responder_documento(doc: Documento, disposition: str):
    headers = {"Content-Disposition": content_disposition(disposition, doc.nome_arquivo)}

    return FileResponse(
        path=caminho_documento(doc),
        media_type=doc.mime_type,
        headers=headers,
    )


@router.get("/me")
def meus_documentos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    docs = (
        db.query(Documento)
        .filter(Documento.user_id == current_user.id)
        .order_by(Documento.criado_em.desc())
        .all()
    )
    return [_fmt(d) for d in docs]


@router.get("/usuario/{user_id}")
def documentos_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    docs = (
        db.query(Documento)
        .filter(Documento.user_id == user_id)
        .order_by(Documento.criado_em.desc())
        .all()
    )
    return [_fmt(d) for d in docs]


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_documento(
    file: UploadFile = File(...),
    tipo: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if tipo == "contracheque" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem enviar contracheques")

    if tipo not in ("atestado", "contracheque"):
        raise HTTPException(status_code=400, detail="Tipo invalido. Use 'atestado' ou 'contracheque'")

    if current_user.role != "admin" and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Voce so pode enviar documentos para si mesmo")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    arquivo_bytes = await file.read()

    if len(arquivo_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Limite: 10 MB")

    mime = file.content_type or "application/octet-stream"
    if mime not in TIPOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail="Tipo de arquivo nao permitido. Aceitos: PDF, JPEG, PNG")

    if not validar_assinatura_arquivo(arquivo_bytes, mime):
        raise HTTPException(status_code=400, detail="Assinatura do arquivo invalida")

    nome_armazenado = gerar_nome_armazenamento(file.filename, mime)
    upload_dir = obter_upload_dir()
    caminho_recebido = obter_diretorio_recebido(target_user) / nome_armazenado
    caminho_recebido.write_bytes(arquivo_bytes)
    caminho_recebido_relativo = caminho_recebido.relative_to(upload_dir).as_posix()

    caminho_enviado = None
    caminho_enviado_relativo = None
    if current_user.role == "admin":
        caminho_enviado = obter_diretorio_enviado(current_user, target_user) / nome_armazenado
        caminho_enviado.write_bytes(arquivo_bytes)
        caminho_enviado_relativo = caminho_enviado.relative_to(upload_dir).as_posix()

    doc = Documento(
        user_id=user_id,
        tipo=tipo,
        nome_arquivo=corrigir_nome_arquivo(file.filename),
        mime_type=mime,
        caminho_arquivo=caminho_recebido_relativo,
        caminho_enviado=caminho_enviado_relativo,
        tamanho=len(arquivo_bytes),
        criado_por_id=current_user.id,
    )

    try:
        db.add(doc)
        db.flush()

        log = Log(
            user_id=current_user.id,
            acao="DOCUMENTO_ENVIADO",
            detalhes=f"{tipo.title()} '{file.filename}' enviado para {target_user.nome}",
        )
        db.add(log)
        db.commit()
        db.refresh(doc)
    except Exception:
        db.rollback()
        if caminho_enviado:
            caminho_enviado.unlink(missing_ok=True)
        caminho_recebido.unlink(missing_ok=True)
        raise

    return _fmt(doc)


@router.get("/{doc_id}/download")
def download_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento nao encontrado")

    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return responder_documento(doc, "attachment")


@router.get("/{doc_id}/visualizar")
def visualizar_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento nao encontrado")

    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return responder_documento(doc, "inline")


@router.delete("/{doc_id}", status_code=status.HTTP_200_OK)
def excluir_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento nao encontrado")

    caminhos_para_excluir = []
    if doc.caminho_arquivo:
        try:
            caminhos_para_excluir.append(caminho_documento(doc))
        except HTTPException:
            pass

    caminho_enviado = caminho_documento_enviado(doc)
    if caminho_enviado:
        caminhos_para_excluir.append(caminho_enviado)

    log = Log(
        user_id=current_user.id,
        acao="DOCUMENTO_EXCLUIDO",
        detalhes=f"Documento '{doc.nome_arquivo}' excluido",
    )
    db.add(log)
    db.delete(doc)
    db.commit()

    for caminho in caminhos_para_excluir:
        caminho.unlink(missing_ok=True)

    return {"detail": "Documento excluido com sucesso"}
