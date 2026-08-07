import math
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.documento import Documento
from app.models.user import User
from app.repositories import documentos_repository
from app.services import log_service
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
CAIXAS_DOCUMENTOS = ("recebidos_pessoais", "recebidos_administracao", "enviados")
MAX_OBSERVACAO_LENGTH = 2000


def validar_permissao_upload(tipo: str, user_id: int, destino_tipo: str, current_user: User) -> None:
    if tipo == "contracheque" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem enviar contracheques")

    if tipo not in TIPOS_DOCUMENTO:
        raise HTTPException(status_code=400, detail="Tipo de documento inválido")

    if destino_tipo not in DESTINOS_DOCUMENTO:
        raise HTTPException(status_code=400, detail="Destino de documento inválido")

    if current_user.role != "admin":
        if destino_tipo != "administracao" or user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Colaboradores só podem enviar documentos para a administração")


def validar_acesso_documento(doc: Documento, current_user: User) -> None:
    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")


def validar_arquivo_upload(arquivo_bytes: bytes, mime: str) -> None:
    if len(arquivo_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Limite: 10 MB")

    if mime not in TIPOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido. Aceitos: PDF, JPEG, PNG")

    if not validar_assinatura_arquivo(arquivo_bytes, mime):
        raise HTTPException(status_code=400, detail="Assinatura do arquivo inválida")


def normalizar_observacao(observacao: str | None) -> str | None:
    texto = observacao.strip() if observacao else ""
    if not texto:
        return None
    if len(texto) > MAX_OBSERVACAO_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"A observação deve ter no máximo {MAX_OBSERVACAO_LENGTH} caracteres",
        )
    return texto


def buscar_usuario(db: Session, user_id: int) -> User:
    user = documentos_repository.obter_usuario_por_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


def buscar_documento(db: Session, doc_id: int) -> Documento:
    doc = documentos_repository.obter_documento_por_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return doc


def listar_documentos_usuario(db: Session, user_id: int) -> list[Documento]:
    return documentos_repository.listar_documentos_por_usuario(db, user_id)


def listar_historico_documentos_paginado(
    db: Session,
    current_user: User,
    caixa: str,
    page: int,
    page_size: int,
    user_id: int | None = None,
) -> dict:
    if caixa not in CAIXAS_DOCUMENTOS:
        raise HTTPException(status_code=400, detail="Caixa de documentos inválida")
    if caixa == "recebidos_administracao" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    if user_id is not None and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    filtro_usuario_id = (
        user_id
        if current_user.role == "admin" and caixa != "recebidos_pessoais"
        else None
    )
    total = documentos_repository.contar_historico(
        db,
        caixa,
        current_user.id,
        filtro_usuario_id,
    )
    items = documentos_repository.listar_historico_paginado(
        db,
        caixa,
        current_user.id,
        filtro_usuario_id,
        (page - 1) * page_size,
        page_size,
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, math.ceil(total / page_size)),
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
    observacao: str | None = None,
) -> Documento:
    validar_permissao_upload(tipo, user_id, destino_tipo, current_user)
    observacao_normalizada = normalizar_observacao(observacao)

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
        observacao=observacao_normalizada,
    )

    try:
        destinatario_nome = target_user.nome if destino_tipo == "usuario" else "Administração"
        log = log_service.construir_log(
            current_user,
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


def registrar_acesso_documento(
    db: Session,
    doc: Documento,
    current_user: User,
    modo: str,
) -> None:
    acao = "DOCUMENTO_BAIXADO" if modo == "download" else "DOCUMENTO_VISUALIZADO"
    log = log_service.construir_log(
        current_user,
        acao=acao,
        detalhes=f"Documento #{doc.id} ('{doc.nome_arquivo}') acessado",
    )
    if log is not None:
        db.add(log)
    db.commit()


def excluir_documento_admin(db: Session, doc_id: int, current_user: User) -> None:
    doc = buscar_documento(db, doc_id)
    if doc.tipo == "termo_equipamentos":
        raise HTTPException(
            status_code=400,
            detail="Termos definitivos de equipamentos não podem ser excluídos pelo módulo de documentos",
        )
    caminhos = caminhos_para_excluir(doc)

    log = log_service.construir_log(
        current_user,
        acao="DOCUMENTO_EXCLUIDO",
        detalhes=f"Documento '{doc.nome_arquivo}' excluído",
    )
    quarentena: list[tuple[Path, Path]] = []
    try:
        for caminho in caminhos:
            if not caminho.exists():
                continue
            temporario = caminho.with_name(f".deleting-{doc.id}-{caminho.name}")
            caminho.replace(temporario)
            quarentena.append((temporario, caminho))

        documentos_repository.excluir_documento_com_log(db, doc, log)
    except Exception:
        db.rollback()
        for temporario, original in reversed(quarentena):
            if temporario.exists():
                temporario.replace(original)
        raise

    for temporario, _ in quarentena:
        try:
            temporario.unlink(missing_ok=True)
        except OSError:
            # A exclusao logica ja foi confirmada; o residual em quarentena
            # pode ser limpo posteriormente sem reexpor o documento.
            pass
