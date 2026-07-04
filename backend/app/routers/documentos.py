from pathlib import Path
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.documento import Documento
from app.models.user import User
from app.models.log import Log
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/documentos", tags=["Documentos"])

MAX_SIZE = 10 * 1024 * 1024  # 10 MB
TIPOS_PERMITIDOS = {"application/pdf", "image/jpeg", "image/png"}


def validar_assinatura_arquivo(conteudo: bytes, mime: str) -> bool:
    if mime == "application/pdf":
        return conteudo.startswith(b"%PDF-")

    if mime == "image/jpeg":
        return conteudo.startswith(b"\xff\xd8\xff")

    if mime == "image/png":
        return conteudo.startswith(b"\x89PNG\r\n\x1a\n")

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


@router.get("/me")
def meus_documentos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(Documento).filter(Documento.user_id == current_user.id).order_by(Documento.criado_em.desc()).all()
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
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    docs = db.query(Documento).filter(Documento.user_id == user_id).order_by(Documento.criado_em.desc()).all()
    return [_fmt(d) for d in docs]


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_documento(
    file: UploadFile = File(...),
    tipo: str = Form(...),  # "atestado" ou "contracheque"
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Atestado: qualquer usuário envia o próprio; admin envia para qualquer um
    # Contracheque: apenas admin pode enviar
    if tipo == "contracheque" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem enviar contracheques")

    if tipo not in ("atestado", "contracheque"):
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'atestado' ou 'contracheque'")

    if current_user.role != "admin" and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você só pode enviar documentos para si mesmo")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    conteudo = await file.read()

    if len(conteudo) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Limite: 10 MB")

    mime = file.content_type or "application/octet-stream"
    if mime not in TIPOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail=f"Tipo de arquivo não permitido. Aceitos: PDF, JPEG, PNG")

    if not validar_assinatura_arquivo(conteudo, mime):
        raise HTTPException(status_code=400, detail="Assinatura do arquivo inválida")

    doc = Documento(
        user_id=user_id,
        tipo=tipo,
        nome_arquivo=corrigir_nome_arquivo(file.filename),
        mime_type=mime,
        conteudo=conteudo,
        tamanho=len(conteudo),
        criado_por_id=current_user.id,
    )
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

    return _fmt(doc)


@router.get("/{doc_id}/download")
def download_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return Response(
        content=doc.conteudo,
        media_type=doc.mime_type,
        headers={"Content-Disposition": content_disposition("attachment", doc.nome_arquivo)},
    )


@router.get("/{doc_id}/visualizar")
def visualizar_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return Response(
        content=doc.conteudo,
        media_type=doc.mime_type,
        headers={"Content-Disposition": content_disposition("inline", doc.nome_arquivo)},
    )


@router.delete("/{doc_id}", status_code=status.HTTP_200_OK)
def excluir_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    log = Log(
        user_id=current_user.id,
        acao="DOCUMENTO_EXCLUIDO",
        detalhes=f"Documento '{doc.nome_arquivo}' excluído",
    )
    db.add(log)
    db.delete(doc)
    db.commit()

    return {"detail": "Documento excluído com sucesso"}
