import base64
import hashlib
import hmac

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


CREDENTIAL_PREFIX = "fernet:"
SENSITIVE_PREFIX = "sensitive:"


def _derive_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _get_credentials_secret() -> str:
    return settings.credentials_encryption_key


def _get_fernet() -> Fernet:
    return Fernet(_derive_key(_get_credentials_secret()))


def criptografar_credencial(senha: str) -> str:
    if senha.startswith(CREDENTIAL_PREFIX):
        return senha

    token = _get_fernet().encrypt(senha.encode("utf-8")).decode("utf-8")
    return f"{CREDENTIAL_PREFIX}{token}"


def descriptografar_credencial(senha_criptografada: str) -> str:
    if not senha_criptografada.startswith(CREDENTIAL_PREFIX):
        return senha_criptografada

    token = senha_criptografada.removeprefix(CREDENTIAL_PREFIX)
    try:
        return _get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Nao foi possivel descriptografar a credencial.") from exc


def criptografar_dado_sensivel(valor: str) -> str:
    if valor.startswith(SENSITIVE_PREFIX):
        return valor
    token = _get_fernet().encrypt(valor.encode("utf-8")).decode("utf-8")
    return f"{SENSITIVE_PREFIX}{token}"


def descriptografar_dado_sensivel(valor: str | None) -> str | None:
    if not valor or not valor.startswith(SENSITIVE_PREFIX):
        return valor
    token = valor.removeprefix(SENSITIVE_PREFIX)
    try:
        return _get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Nao foi possivel descriptografar o dado sensivel.") from exc


def hash_dado_sensivel(valor: str) -> str:
    return hmac.new(
        _get_credentials_secret().encode("utf-8"),
        valor.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
