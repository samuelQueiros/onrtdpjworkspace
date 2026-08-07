import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _ler_secret_arquivo(nome_var_arquivo: str, fallback_env: str | None = None) -> str | None:
    """Le um valor sensivel a partir de um arquivo montado (Docker/Portainer secret).

    `nome_var_arquivo` deve apontar (via env var) para o caminho do arquivo montado, ex.
    GMAIL_APP_PASSWORD_FILE=/run/secrets/gmail_app_password. Se o arquivo nao existir (ex.
    ambiente local sem Docker secrets), cai para a env var simples `fallback_env`, se informada.
    Nunca logar o valor retornado.
    """
    caminho = os.getenv(nome_var_arquivo)
    if caminho:
        arquivo = Path(caminho)
        if arquivo.is_file():
            return arquivo.read_text(encoding="utf-8").strip()
    if fallback_env:
        return os.getenv(fallback_env)
    return None


class Settings:
    @property
    def environment(self) -> str:
        return os.getenv("ENVIRONMENT", "development")

    @property
    def database_url(self) -> str:
        return os.getenv(
            "DATABASE_URL",
            "postgresql://ferias:ferias@localhost:5432/ferias",
        )

    @property
    def frontend_url(self) -> str:
        return os.getenv("FRONTEND_URL", "http://localhost:5173")

    @property
    def admin_email(self) -> str | None:
        return os.getenv("ADMIN_EMAIL")

    @property
    def admin_password(self) -> str | None:
        return os.getenv("ADMIN_PASSWORD")

    @property
    def admin_name(self) -> str:
        return os.getenv("ADMIN_NAME", "Administrador")

    @property
    def secret_key(self) -> str:
        secret = os.getenv("SECRET_KEY")
        if secret:
            return secret

        if self.environment == "production":
            raise RuntimeError("SECRET_KEY nao esta configurada.")

        return "chave-secreta-padrao-troque-em-producao"

    @property
    def access_token_expire_minutes(self) -> int:
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    @property
    def database_pool_size(self) -> int:
        return int(os.getenv("DATABASE_POOL_SIZE", "10"))

    @property
    def database_max_overflow(self) -> int:
        return int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))

    @property
    def database_pool_timeout_seconds(self) -> int:
        return int(os.getenv("DATABASE_POOL_TIMEOUT_SECONDS", "30"))

    @property
    def database_pool_recycle_seconds(self) -> int:
        return int(os.getenv("DATABASE_POOL_RECYCLE_SECONDS", "1800"))

    @property
    def database_connect_timeout_seconds(self) -> int:
        return int(os.getenv("DATABASE_CONNECT_TIMEOUT_SECONDS", "10"))

    @property
    def database_statement_timeout_ms(self) -> int:
        return int(os.getenv("DATABASE_STATEMENT_TIMEOUT_MS", "30000"))

    @property
    def cookie_secure(self) -> bool:
        valor = os.getenv("COOKIE_SECURE")
        if valor is None:
            return self.environment == "production"
        return valor.strip().lower() in {"1", "true", "sim", "yes", "on"}

    @property
    def trusted_proxy_ips(self) -> set[str]:
        valor = os.getenv("TRUSTED_PROXY_IPS", "")
        return {item.strip() for item in valor.split(",") if item.strip()}

    @property
    def allow_insecure_production_cookie(self) -> bool:
        valor = os.getenv("ALLOW_INSECURE_PRODUCTION_COOKIE", "false")
        return valor.strip().lower() in {"1", "true", "sim", "yes", "on"}

    def validate_runtime(self) -> None:
        secret_key = self.secret_key
        credentials_key = self.credentials_encryption_key
        if self.environment == "production":
            if len(secret_key) < 32 or "troque" in secret_key.lower():
                raise RuntimeError("SECRET_KEY deve ter pelo menos 32 caracteres e nao pode ser um placeholder.")
            if len(credentials_key) < 32 or "troque" in credentials_key.lower():
                raise RuntimeError(
                    "CREDENTIALS_ENCRYPTION_KEY deve ter pelo menos 32 caracteres e nao pode ser um placeholder."
                )
            if secret_key == credentials_key:
                raise RuntimeError("SECRET_KEY e CREDENTIALS_ENCRYPTION_KEY devem ser diferentes.")
            if "://ferias:ferias@" in self.database_url:
                raise RuntimeError("DATABASE_URL de producao nao pode usar as credenciais padrao.")
            if self.admin_password and (
                len(self.admin_password) < 12
                or "troque" in self.admin_password.lower()
                or self.admin_password == "Teste@123456"
            ):
                raise RuntimeError(
                    "ADMIN_PASSWORD deve ter pelo menos 12 caracteres e nao pode ser um placeholder."
                )
        if (
            self.environment == "production"
            and not self.cookie_secure
            and not self.allow_insecure_production_cookie
        ):
            raise RuntimeError(
                "COOKIE_SECURE deve ser true em producao. "
                "Use ALLOW_INSECURE_PRODUCTION_COOKIE=true somente em uma rede HTTP controlada."
            )
        if self.environment == "production":
            if not self.gmail_user or not self.gmail_app_password:
                raise RuntimeError(
                    "GMAIL_USER e GMAIL_APP_PASSWORD (ou GMAIL_APP_PASSWORD_FILE) "
                    "sao obrigatorios para o envio de lembretes de ferias."
                )
            if not self.public_app_url:
                raise RuntimeError("PUBLIC_APP_URL nao esta configurada.")

    @property
    def credentials_encryption_key(self) -> str:
        secret = os.getenv("CREDENTIALS_ENCRYPTION_KEY")
        if secret:
            return secret

        if self.environment == "production":
            raise RuntimeError("CREDENTIALS_ENCRYPTION_KEY nao esta configurada.")

        return os.getenv("SECRET_KEY", "chave-local-para-credenciais")

    @property
    def upload_dir(self) -> Path:
        return Path(os.getenv("UPLOAD_DIR", "data/uploads")).resolve()

    @property
    def gmail_user(self) -> str | None:
        return os.getenv("GMAIL_USER")

    @property
    def gmail_app_password(self) -> str | None:
        return _ler_secret_arquivo("GMAIL_APP_PASSWORD_FILE", fallback_env="GMAIL_APP_PASSWORD")

    @property
    def public_app_url(self) -> str | None:
        """Dominio HTTPS publico real (alcancavel da internet), usado para montar a URL do
        pixel de rastreio de e-mail. Diferente de `frontend_url`, que hoje so serve para CORS
        e pode ser um hostname interno de rede Docker."""
        valor = os.getenv("PUBLIC_APP_URL")
        return valor.rstrip("/") if valor else None

    @property
    def envios_monitoramento_intervalo_minutos(self) -> int:
        return int(os.getenv("ENVIOS_MONITORAMENTO_INTERVALO_MINUTOS", "20"))


settings = Settings()
