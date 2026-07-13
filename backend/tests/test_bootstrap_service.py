import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.services import bootstrap_service


class BootstrapServiceTests(unittest.TestCase):
    def setUp(self):
        self.old_admin_email = os.environ.get("ADMIN_EMAIL")
        self.old_admin_password = os.environ.get("ADMIN_PASSWORD")
        self.old_admin_name = os.environ.get("ADMIN_NAME")
        self.old_environment = os.environ.get("ENVIRONMENT")

    def tearDown(self):
        self._restore_env("ADMIN_EMAIL", self.old_admin_email)
        self._restore_env("ADMIN_PASSWORD", self.old_admin_password)
        self._restore_env("ADMIN_NAME", self.old_admin_name)
        self._restore_env("ENVIRONMENT", self.old_environment)

    def _restore_env(self, key, value):
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    def test_garantir_admin_inicial_ignora_quando_ja_existe(self):
        with (
            patch("app.services.bootstrap_service.bootstrap_repository.obter_admin", return_value=SimpleNamespace(id=1)),
            patch("app.services.bootstrap_service.bootstrap_repository.salvar_admin_com_log") as salvar,
        ):
            response = bootstrap_service.garantir_admin_inicial(SimpleNamespace())

        self.assertEqual(response, "admin_existente")
        salvar.assert_not_called()

    def test_garantir_admin_inicial_retorna_nao_configurado_sem_env(self):
        os.environ.pop("ADMIN_EMAIL", None)
        os.environ.pop("ADMIN_PASSWORD", None)

        with patch("app.services.bootstrap_service.bootstrap_repository.obter_admin", return_value=None):
            response = bootstrap_service.garantir_admin_inicial(SimpleNamespace())

        self.assertEqual(response, "admin_nao_configurado")

    def test_garantir_admin_inicial_cria_admin_com_log(self):
        os.environ["ENVIRONMENT"] = "development"
        os.environ["ADMIN_EMAIL"] = "admin@sistema.com"
        os.environ["ADMIN_PASSWORD"] = "senha-segura"
        os.environ["ADMIN_NAME"] = "Administrador"

        with (
            patch("app.services.bootstrap_service.bootstrap_repository.obter_admin", return_value=None),
            patch("app.services.bootstrap_service.hash_senha", return_value="hash"),
            patch("app.services.bootstrap_service.bootstrap_repository.salvar_admin_com_log") as salvar,
        ):
            response = bootstrap_service.garantir_admin_inicial(SimpleNamespace())

        admin = salvar.call_args.args[1]
        log = salvar.call_args.args[2]
        self.assertEqual(response, "admin_criado")
        self.assertEqual(admin.email, "admin@sistema.com")
        self.assertEqual(admin.senha_hash, "hash")
        self.assertEqual(log.acao, "USUARIO_CRIADO")

    def test_producao_rejeita_senha_admin_fraca(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ["ADMIN_EMAIL"] = "admin@sistema.com"
        os.environ["ADMIN_PASSWORD"] = "admin123"
        with patch("app.services.bootstrap_service.bootstrap_repository.obter_admin", return_value=None):
            with self.assertRaises(RuntimeError):
                bootstrap_service.garantir_admin_inicial(SimpleNamespace())


if __name__ == "__main__":
    unittest.main()
