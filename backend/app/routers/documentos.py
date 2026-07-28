from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.documento import Documento
from app.models.user import User
from app.schemas.common import MensagemOut
from app.schemas.documento import DocumentoOut, HistoricoDocumentosOut
from app.services.documentos_service import (
    buscar_documento,
    buscar_usuario,
    criar_documento_upload,
    excluir_documento_admin,
    listar_documentos_usuario,
    listar_historico_documentos,
    validar_acesso_documento,
)
from app.storage.documentos_storage import (
    caminho_documento,
    content_disposition,
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
        "criado_por_id": doc.criado_por_id,
        "criado_por_nome": doc.criado_por.nome if doc.criado_por else "Sistema",
        "destino_tipo": doc.destino_tipo,
        "destinatario_id": doc.destinatario_id,
        "destinatario_nome": (
            doc.destinatario.nome
            if doc.destino_tipo == "usuario" and doc.destinatario
            else "Administração"
        ),
        "criado_em": doc.criado_em,
    }


def responder_documento(doc: Documento, disposition: str):
    headers = {"Content-Disposition": content_disposition(disposition, doc.nome_arquivo)}

    return FileResponse(
        path=caminho_documento(doc),
        media_type=doc.mime_type,
        headers=headers,
    )


@router.get("/me", response_model=list[DocumentoOut])
def meus_documentos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    docs = listar_documentos_usuario(db, current_user.id)
    return [_fmt(d) for d in docs]


@router.get("/historico", response_model=HistoricoDocumentosOut)
def historico_documentos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    historico = listar_historico_documentos(db, current_user)
    return {
        "recebidos_pessoais": [_fmt(doc) for doc in historico["recebidos_pessoais"]],
        "recebidos_administracao": [_fmt(doc) for doc in historico["recebidos_administracao"]],
        "enviados": [_fmt(doc) for doc in historico["enviados"]],
    }


@router.get("/usuario/{user_id}", response_model=list[DocumentoOut])
def documentos_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    buscar_usuario(db, user_id)
    docs = listar_documentos_usuario(db, user_id)
    return [_fmt(d) for d in docs]


@router.post("/upload", response_model=DocumentoOut, status_code=status.HTTP_201_CREATED)
async def upload_documento(
    file: UploadFile = File(...),
    tipo: str = Form(...),
    user_id: int = Form(...),
    destino_tipo: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = await criar_documento_upload(db, file, tipo, user_id, destino_tipo, current_user)
    return _fmt(doc)


@router.get("/{doc_id}/download")
def download_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = buscar_documento(db, doc_id)
    validar_acesso_documento(doc, current_user)

    return responder_documento(doc, "attachment")


@router.get("/{doc_id}/visualizar")
def visualizar_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = buscar_documento(db, doc_id)
    validar_acesso_documento(doc, current_user)

    return responder_documento(doc, "inline")


@router.delete("/{doc_id}", response_model=MensagemOut, status_code=status.HTTP_200_OK)
def excluir_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    excluir_documento_admin(db, doc_id, current_user)
    return {"detail": "Documento excluido com sucesso"}
