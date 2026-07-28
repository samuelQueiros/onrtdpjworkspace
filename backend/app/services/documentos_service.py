from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.documento import Documento
from app.models.log import Log
from app.models.user import User
from app.repositories import documentos_repository
from app.storage.documentos_storage import (
    MAX_SIZE,
    TIPOS_PERMITIDOS,
    caminho_documento,
    caminho_documento_enviado,
    corrigir_nome_arquivo,
    gerar_nome_armazenamento,
    obter_diretorio_enviado,
    obter_diretorio_enviado_administracao,
    obter_diretorio_recebido,
    obter_diretorio_recebido_administracao,
    obter_upload_dir,
    validar_assinatura_arquivo,
)

TIPOS_DOCUMENTO = ("atestado", "contracheque", "outro")
DESTINOS_DOCUMENTO = ("usuario", "administracao")


def validar_permissao_upload(tipo: str, user_id: int, destino_tipo: str, current_user: User) -> None:
    if tipo == "contracheque" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem enviar contracheques")

    if tipo not in TIPOS_DOCUMENTO:
        raise HTTPException(status_code=400, detail="Tipo de documento invalido")

    if destino_tipo not in DESTINOS_DOCUMENTO:
        raise HTTPException(status_code=400, detail="Destino de documento invalido")

    if current_user.role != "admin":
        if destino_tipo != "administracao" or user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Colaboradores so podem enviar documentos para a administracao")


def validar_acesso_documento(doc: Documento, current_user: User) -> None:
    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")


def validar_arquivo_upload(arquivo_bytes: bytes, mime: str) -> None:
    if len(arquivo_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Limite: 10 MB")

    if mime not in TIPOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail="Tipo de arquivo nao permitido. Aceitos: PDF, JPEG, PNG")

    if not validar_assinatura_arquivo(arquivo_bytes, mime):
        raise HTTPException(status_code=400, detail="Assinatura do arquivo invalida")


def buscar_usuario(db: Session, user_id: int) -> User:
    user = documentos_repository.obter_usuario_por_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return user


def buscar_documento(db: Session, doc_id: int) -> Documento:
    doc = documentos_repository.obter_documento_por_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento nao encontrado")
    return doc


def listar_documentos_usuario(db: Session, user_id: int) -> list[Documento]:
    return documentos_repository.listar_documentos_por_usuario(db, user_id)


def listar_historico_documentos(db: Session, current_user: User) -> dict[str, list[Documento]]:
    enviados = documentos_repository.listar_documentos_criados_por(
        db, current_user.id, ["atestado", "contracheque", "outro", "termo_equipamentos"]
    )
    recebidos_pessoais = documentos_repository.listar_documentos_recebidos_pessoais(db, current_user.id)
    recebidos_administracao = (
        documentos_repository.listar_documentos_recebidos_administracao(db)
        if current_user.role == "admin"
        else []
    )
    return {
        "recebidos_pessoais": recebidos_pessoais,
        "recebidos_administracao": recebidos_administracao,
        "enviados": enviados,
    }


def salvar_arquivo_upload(
    arquivo_bytes: bytes,
    nome_original: str | None,
    mime: str,
    target_user: User,
    current_user: User,
    destino_tipo: str,
) -> tuple[str, str | None, Path, Path | None]:
    nome_armazenado = gerar_nome_armazenamento(nome_original, mime)
    upload_dir = obter_upload_dir()

    diretorio_recebido = (
        obter_diretorio_recebido(target_user)
        if destino_tipo == "usuario"
        else obter_diretorio_recebido_administracao(current_user)
    )
    diretorio_enviado = (
        obter_diretorio_enviado(current_user, target_user)
        if destino_tipo == "usuario"
        else obter_diretorio_enviado_administracao(current_user)
    )
    caminho_recebido = diretorio_recebido / nome_armazenado
    caminho_enviado = diretorio_enviado / nome_armazenado

    caminho_recebido.write_bytes(arquivo_bytes)
    try:
        caminho_enviado.write_bytes(arquivo_bytes)
    except Exception:
        caminho_recebido.unlink(missing_ok=True)
        raise

    caminho_recebido_relativo = caminho_recebido.relative_to(upload_dir).as_posix()
    caminho_enviado_relativo = caminho_enviado.relative_to(upload_dir).as_posix()
    return caminho_recebido_relativo, caminho_enviado_relativo, caminho_recebido, caminho_enviado


async def criar_documento_upload(
    db: Session,
    file: UploadFile,
    tipo: str,
    user_id: int,
    destino_tipo: str,
    current_user: User,
) -> Documento:
    validar_permissao_upload(tipo, user_id, destino_tipo, current_user)

    target_user = buscar_usuario(db, user_id)
    arquivo_bytes = await file.read(MAX_SIZE + 1)
    mime = file.content_type or "application/octet-stream"
    validar_arquivo_upload(arquivo_bytes, mime)

    (
        caminho_relativo,
        caminho_legado_relativo,
        caminho_principal,
        caminho_legado,
    ) = salvar_arquivo_upload(
        arquivo_bytes=arquivo_bytes,
        nome_original=file.filename,
        mime=mime,
        target_user=target_user,
        current_user=current_user,
        destino_tipo=destino_tipo,
    )

    doc = Documento(
        user_id=user_id,
        tipo=tipo,
        nome_arquivo=corrigir_nome_arquivo(file.filename),
        mime_type=mime,
        caminho_arquivo=caminho_relativo,
        caminho_enviado=caminho_legado_relativo,
        tamanho=len(arquivo_bytes),
        criado_por_id=current_user.id,
        destino_tipo=destino_tipo,
        destinatario_id=user_id if destino_tipo == "usuario" else None,
    )

    try:
        destinatario_nome = target_user.nome if destino_tipo == "usuario" else "Administração"
        log = Log(
            user_id=current_user.id,
            acao="DOCUMENTO_ENVIADO",
            detalhes=f"{tipo.title()} '{file.filename}' enviado para {destinatario_nome}",
        )
        documentos_repository.salvar_documento_com_log(db, doc, log)
    except Exception:
        db.rollback()
        if caminho_legado:
            caminho_legado.unlink(missing_ok=True)
        caminho_principal.unlink(missing_ok=True)
        raise

    return doc


def caminhos_para_excluir(doc: Documento) -> list[Path]:
    caminhos = []
    if doc.caminho_arquivo:
        try:
            caminhos.append(caminho_documento(doc))
        except HTTPException:
            pass

    caminho_enviado = caminho_documento_enviado(doc)
    if caminho_enviado:
        caminhos.append(caminho_enviado)

    return caminhos


def excluir_documento_admin(db: Session, doc_id: int, current_user: User) -> None:
    doc = buscar_documento(db, doc_id)
    if doc.tipo == "termo_equipamentos":
        raise HTTPException(
            status_code=400,
            detail="Termos definitivos de equipamentos nao podem ser excluidos pelo modulo de documentos",
        )
    caminhos = caminhos_para_excluir(doc)

    log = Log(
        user_id=current_user.id,
        acao="DOCUMENTO_EXCLUIDO",
        detalhes=f"Documento '{doc.nome_arquivo}' excluido",
    )
    documentos_repository.excluir_documento_com_log(db, doc, log)

    for caminho in caminhos:
        caminho.unlink(missing_ok=True)
