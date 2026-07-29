from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_senha
from app.models.log import Log
from app.models.user import User
from app.repositories import bootstrap_repository
from app.storage.documentos_storage import inicializar_diretorios_upload


def inicializar_uploads() -> None:
    inicializar_diretorios_upload()


def garantir_admin_inicial(db: Session) -> str:
    if bootstrap_repository.obter_admin(db):
        return "admin_existente"

    admin_email = settings.admin_email
    admin_password = settings.admin_password

    if not admin_email or not admin_password:
        return "admin_nao_configurado"

    if len(admin_password) < 8:
        raise RuntimeError("ADMIN_PASSWORD deve ter pelo menos 8 caracteres.")
    if settings.environment == "production":
        fracas = {"admin123", "password", "12345678", "administrador"}
        if len(admin_password) < 12 or admin_password.lower() in fracas:
            raise RuntimeError(
                "ADMIN_PASSWORD deve ser forte e ter pelo menos 12 caracteres em producao."
            )

    admin = User(
        nome=settings.admin_name,
        email=admin_email.strip().lower(),
        senha_hash=hash_senha(admin_password),
        role="admin",
        dias_totais=30,
        must_change_password=False,
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
