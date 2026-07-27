import os
import unittest

from app.core.config import Settings


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
            "CREATE_TEST_USERS",
            "TEST_USER_PASSWORD",
        ]
        self.old_values = {key: os.environ.get(key) for key in self.keys}

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
        self.assertFalse(settings.create_test_users)
        self.assertIsNone(settings.test_user_password)

    def test_seed_de_usuarios_pode_ser_habilitado(self):
        os.environ["CREATE_TEST_USERS"] = "true"
        os.environ["TEST_USER_PASSWORD"] = "senha-de-teste"

        settings = Settings()

        self.assertTrue(settings.create_test_users)
        self.assertEqual(settings.test_user_password, "senha-de-teste")

    def test_cookie_secure_pode_ser_configurado_em_http_controlado(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ["COOKIE_SECURE"] = "false"
        self.assertFalse(Settings().cookie_secure)

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


if __name__ == "__main__":
    unittest.main()
