from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.documento import Documento
from app.models.log import Log
from app.models.user import User
from app.storage.documentos_storage import (
    MAX_SIZE,
    TIPOS_PERMITIDOS,
    caminho_documento,
    caminho_documento_enviado,
    content_disposition,
    corrigir_nome_arquivo,
    gerar_nome_armazenamento,
    obter_diretorio_enviado,
    obter_diretorio_recebido,
    obter_upload_dir,
    validar_assinatura_arquivo,
)

router = APIRouter(prefix="/documentos", tags=["Documentos"])


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
