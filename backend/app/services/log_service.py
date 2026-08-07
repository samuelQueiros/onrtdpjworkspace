from app.models.log import Log
from app.models.user import User


def construir_log(current_user: User, **kwargs) -> Log | None:
    """Constrói um Log de auditoria, exceto quando o ator é o admin de sistema.

    O admin de sistema (User.is_sistema) deve ser completamente invisível para
    os demais usuários, inclusive na trilha de auditoria: nenhuma ação feita
    por ele deve gerar um registro em `logs`.
    """
    if getattr(current_user, "is_sistema", False):
        return None
    return Log(user_id=current_user.id, **kwargs)
