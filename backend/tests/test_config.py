import os
import tempfile
import unittest

from app.core.config import Settings, _ler_secret_arquivo


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.keys = [
            "ENVIRONMENT",
            "DATABASE_URL",
            "FRONTEND_URL",
            "ADMIN_EMAIL",
            "ADMIN_PASSWORD",
            "ADMIN_NAME",
            "SECRET_KEY",
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "CREDENTIALS_ENCRYPTION_KEY",
            "UPLOAD_DIR",
            "COOKIE_SECURE",
            "ALLOW_INSECURE_PRODUCTION_COOKIE",
            "TRUSTED_PROXY_IPS",
            "GMAIL_USER",
            "GMAIL_APP_PASSWORD",
            "GMAIL_APP_PASSWORD_FILE",
            "PUBLIC_APP_URL",
        ]
        self.old_values = {key: os.environ.get(key) for key in self.keys}

    def _producao_valida_env(self) -> dict:
        return {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "segredo-de-producao-com-mais-de-32-caracteres",
            "CREDENTIALS_ENCRYPTION_KEY": "criptografia-producao-distinta-com-32-caracteres",
            "DATABASE_URL": "postgresql://app:senha-forte@db:5432/ferias",
            "ADMIN_PASSWORD": "SenhaInicialForte1!",
            "COOKIE_SECURE": "false",
            "ALLOW_INSECURE_PRODUCTION_COOKIE": "true",
            "GMAIL_USER": "lembretes@empresa.com.br",
            "GMAIL_APP_PASSWORD": "senha-de-app-16-digitos",
            "PUBLIC_APP_URL": "https://rh.empresa.com.br",
        }

    def tearDown(self):
        for key, value in self.old_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_defaults_de_desenvolvimento(self):
        for key in self.keys:
            os.environ.pop(key, None)

        settings = Settings()

        self.assertEqual(settings.environment, "development")
        self.assertEqual(settings.frontend_url, "http://localhost:5173")
        self.assertEqual(settings.access_token_expire_minutes, 480)
        self.assertEqual(settings.secret_key, "chave-secreta-padrao-troque-em-producao")
        self.assertEqual(settings.credentials_encryption_key, "chave-local-para-credenciais")
        self.assertFalse(settings.cookie_secure)

    def test_cookie_secure_pode_ser_configurado_em_http_controlado(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ["COOKIE_SECURE"] = "false"
        self.assertFalse(Settings().cookie_secure)

    def test_runtime_rejeita_cookie_inseguro_em_producao_sem_excecao(self):
        env = self._producao_valida_env()
        env["ALLOW_INSECURE_PRODUCTION_COOKIE"] = "false"
        os.environ.update(env)
        with self.assertRaises(RuntimeError):
            Settings().validate_runtime()

    def test_runtime_permite_http_controlado_quando_explicito(self):
        os.environ.update(self._producao_valida_env())
        Settings().validate_runtime()

    def test_runtime_exige_credenciais_de_email_em_producao(self):
        env = self._producao_valida_env()
        env.pop("GMAIL_USER")
        env.pop("GMAIL_APP_PASSWORD")
        os.environ.pop("GMAIL_USER", None)
        os.environ.pop("GMAIL_APP_PASSWORD", None)
        os.environ.update(env)
        with self.assertRaises(RuntimeError):
            Settings().validate_runtime()

    def test_runtime_exige_public_app_url_em_producao(self):
        env = self._producao_valida_env()
        env.pop("PUBLIC_APP_URL")
        os.environ.pop("PUBLIC_APP_URL", None)
        os.environ.update(env)
        with self.assertRaises(RuntimeError):
            Settings().validate_runtime()

    def test_producao_exige_secret_key(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ.pop("SECRET_KEY", None)

        with self.assertRaises(RuntimeError):
            Settings().secret_key

    def test_producao_exige_chave_de_credenciais(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ.pop("CREDENTIALS_ENCRYPTION_KEY", None)

        with self.assertRaises(RuntimeError):
            Settings().credentials_encryption_key

    def test_ler_secret_arquivo_le_conteudo_do_arquivo_montado(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as arquivo:
            arquivo.write("senha-de-app-16-digitos\n")
            caminho = arquivo.name
        try:
            os.environ["GMAIL_APP_PASSWORD_FILE"] = caminho
            self.assertEqual(
                _ler_secret_arquivo("GMAIL_APP_PASSWORD_FILE"),
                "senha-de-app-16-digitos",
            )
        finally:
            os.remove(caminho)

    def test_ler_secret_arquivo_cai_para_fallback_quando_arquivo_nao_existe(self):
        os.environ["GMAIL_APP_PASSWORD_FILE"] = "/caminho/que/nao/existe.txt"
        os.environ["GMAIL_APP_PASSWORD"] = "valor-do-fallback"
        self.assertEqual(
            _ler_secret_arquivo("GMAIL_APP_PASSWORD_FILE", fallback_env="GMAIL_APP_PASSWORD"),
            "valor-do-fallback",
        )

    def test_ler_secret_arquivo_retorna_none_sem_arquivo_nem_fallback(self):
        os.environ.pop("GMAIL_APP_PASSWORD_FILE", None)
        self.assertIsNone(_ler_secret_arquivo("GMAIL_APP_PASSWORD_FILE"))


if __name__ == "__main__":
    unittest.main()
