from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_senha, verificar_senha
from app.models.log import Log
from app.models.user import User
from app.repositories import bootstrap_repository, users_repository
from app.storage.documentos_storage import inicializar_diretorios_upload


def inicializar_uploads() -> None:
    inicializar_diretorios_upload()


def _validar_forca_admin_password(admin_password: str) -> None:
    if len(admin_password) < 8:
        raise RuntimeError("ADMIN_PASSWORD deve ter pelo menos 8 caracteres.")
    if settings.environment == "production":
        fracas = {"admin123", "password", "12345678", "administrador"}
        if len(admin_password) < 12 or admin_password.lower() in fracas:
            raise RuntimeError(
                "ADMIN_PASSWORD deve ser forte e ter pelo menos 12 caracteres em producao."
            )


def garantir_admin_inicial(db: Session) -> str:
    """Cria o admin inicial ou sincroniza sua senha a partir de ADMIN_EMAIL/ADMIN_PASSWORD.

    ADMIN_EMAIL/ADMIN_PASSWORD sao a fonte da verdade para essa conta especifica:
    a cada startup, se ja existir um usuario admin com esse e-mail e a senha
    configurada for diferente da atual, a senha e sincronizada (permite recuperar
    o acesso trocando a variavel de ambiente e reiniciando o container).
    """
    admin_email = settings.admin_email
    admin_password = settings.admin_password

    if not admin_email or not admin_password:
        return "admin_nao_configurado"

    _validar_forca_admin_password(admin_password)
    admin_email = admin_email.strip().lower()

    usuario_existente = users_repository.obter_usuario_por_email(db, admin_email)

    if usuario_existente is None:
        admin = User(
            nome=settings.admin_name,
            email=admin_email,
            senha_hash=hash_senha(admin_password),
            role="admin",
            dias_totais=30,
            must_change_password=False,
            is_sistema=True,
        )
        log = Log(
            user_id=None,
            acao="USUARIO_CRIADO",
            detalhes="Administrador inicial criado automaticamente.",
        )
        bootstrap_repository.salvar_admin_com_log(db, admin, log, commit=False)

        from app.services.ferias_service import registrar_saldo_inicial

        registrar_saldo_inicial(db, admin, 30, admin.id, commit=False)
        db.commit()
        db.refresh(admin)
        return "admin_criado"

    if usuario_existente.role != "admin":
        # O e-mail configurado em ADMIN_EMAIL pertence a um colaborador comum:
        # nunca promove automaticamente, apenas avisa.
        return "admin_email_pertence_a_usuario_nao_admin"

    if verificar_senha(admin_password, usuario_existente.senha_hash):
        if not usuario_existente.is_sistema:
            usuario_existente.is_sistema = True
            db.commit()
        return "admin_existente"

    usuario_existente.senha_hash = hash_senha(admin_password)
    usuario_existente.ativo = True
    usuario_existente.must_change_password = False
    usuario_existente.is_sistema = True
    usuario_existente.token_version += 1  # revoga sessoes emitidas com a senha antiga
    log = Log(
        user_id=usuario_existente.id,
        acao="ADMIN_SENHA_SINCRONIZADA_VIA_ENV",
        detalhes="Senha do administrador sincronizada a partir de ADMIN_PASSWORD no startup.",
    )
    bootstrap_repository.salvar_admin_com_log(db, usuario_existente, log, commit=False)
    db.commit()
    db.refresh(usuario_existente)
    return "admin_senha_sincronizada"
