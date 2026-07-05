import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


CREDENTIAL_PREFIX = "fernet:"


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
