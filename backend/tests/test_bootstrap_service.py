import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

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

    def test_garantir_admin_inicial_retorna_nao_configurado_sem_env(self):
        os.environ.pop("ADMIN_EMAIL", None)
        os.environ.pop("ADMIN_PASSWORD", None)

        response = bootstrap_service.garantir_admin_inicial(MagicMock())

        self.assertEqual(response, "admin_nao_configurado")

    def test_garantir_admin_inicial_cria_admin_quando_nao_existe(self):
        os.environ["ENVIRONMENT"] = "development"
        os.environ["ADMIN_EMAIL"] = "admin@sistema.com"
        os.environ["ADMIN_PASSWORD"] = "senha-segura"
        os.environ["ADMIN_NAME"] = "Administrador"

        with (
            patch("app.services.bootstrap_service.users_repository.obter_usuario_por_email", return_value=None),
            patch("app.services.bootstrap_service.hash_senha", return_value="hash"),
            patch("app.services.bootstrap_service.bootstrap_repository.salvar_admin_com_log") as salvar,
            patch("app.services.ferias_service.registrar_saldo_inicial"),
        ):
            response = bootstrap_service.garantir_admin_inicial(MagicMock())

        admin = salvar.call_args.args[1]
        log = salvar.call_args.args[2]
        self.assertEqual(response, "admin_criado")
        self.assertEqual(admin.email, "admin@sistema.com")
        self.assertEqual(admin.senha_hash, "hash")
        self.assertIsNone(log)

    def test_garantir_admin_inicial_nao_altera_quando_senha_ja_bate(self):
        os.environ["ENVIRONMENT"] = "development"
        os.environ["ADMIN_EMAIL"] = "admin@sistema.com"
        os.environ["ADMIN_PASSWORD"] = "senha-atual"

        admin_existente = SimpleNamespace(
            id=1, role="admin", senha_hash="hash-atual", token_version=0,
            ativo=True, must_change_password=False, is_sistema=True,
        )

        with (
            patch(
                "app.services.bootstrap_service.users_repository.obter_usuario_por_email",
                return_value=admin_existente,
            ),
            patch("app.services.bootstrap_service.verificar_senha", return_value=True),
            patch("app.services.bootstrap_service.bootstrap_repository.salvar_admin_com_log") as salvar,
        ):
            response = bootstrap_service.garantir_admin_inicial(MagicMock())

        self.assertEqual(response, "admin_existente")
        salvar.assert_not_called()
        self.assertEqual(admin_existente.token_version, 0)

    def test_garantir_admin_inicial_marca_is_sistema_em_admin_pre_existente(self):
        os.environ["ENVIRONMENT"] = "development"
        os.environ["ADMIN_EMAIL"] = "admin@sistema.com"
        os.environ["ADMIN_PASSWORD"] = "senha-atual"

        admin_existente = SimpleNamespace(
            id=1, role="admin", senha_hash="hash-atual", token_version=0,
            ativo=True, must_change_password=False, is_sistema=False,
        )
        db = MagicMock()

        with (
            patch(
                "app.services.bootstrap_service.users_repository.obter_usuario_por_email",
                return_value=admin_existente,
            ),
            patch("app.services.bootstrap_service.verificar_senha", return_value=True),
        ):
            response = bootstrap_service.garantir_admin_inicial(db)

        self.assertEqual(response, "admin_existente")
        self.assertTrue(admin_existente.is_sistema)
        db.commit.assert_called_once()

    def test_garantir_admin_inicial_sincroniza_senha_quando_diferente(self):
        os.environ["ENVIRONMENT"] = "development"
        os.environ["ADMIN_EMAIL"] = "admin@sistema.com"
        os.environ["ADMIN_PASSWORD"] = "senha-nova-do-env"

        admin_existente = SimpleNamespace(
            id=1, role="admin", senha_hash="hash-antigo", token_version=3,
            ativo=True, must_change_password=True, is_sistema=False,
        )

        with (
            patch(
                "app.services.bootstrap_service.users_repository.obter_usuario_por_email",
                return_value=admin_existente,
            ),
            patch("app.services.bootstrap_service.verificar_senha", return_value=False),
            patch("app.services.bootstrap_service.hash_senha", return_value="hash-novo"),
            patch("app.services.bootstrap_service.bootstrap_repository.salvar_admin_com_log") as salvar,
        ):
            response = bootstrap_service.garantir_admin_inicial(MagicMock())

        self.assertEqual(response, "admin_senha_sincronizada")
        self.assertEqual(admin_existente.senha_hash, "hash-novo")
        self.assertEqual(admin_existente.token_version, 4)
        self.assertFalse(admin_existente.must_change_password)
        self.assertTrue(admin_existente.is_sistema)
        log = salvar.call_args.args[2]
        self.assertIsNone(log)

    def test_garantir_admin_inicial_nao_promove_usuario_nao_admin(self):
        os.environ["ENVIRONMENT"] = "development"
        os.environ["ADMIN_EMAIL"] = "colaborador@sistema.com"
        os.environ["ADMIN_PASSWORD"] = "senha-do-env"

        usuario_comum = SimpleNamespace(id=9, role="user")

        with (
            patch(
                "app.services.bootstrap_service.users_repository.obter_usuario_por_email",
                return_value=usuario_comum,
            ),
            patch("app.services.bootstrap_service.bootstrap_repository.salvar_admin_com_log") as salvar,
        ):
            response = bootstrap_service.garantir_admin_inicial(MagicMock())

        self.assertEqual(response, "admin_email_pertence_a_usuario_nao_admin")
        salvar.assert_not_called()

    def test_producao_rejeita_senha_admin_fraca(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ["ADMIN_EMAIL"] = "admin@sistema.com"
        os.environ["ADMIN_PASSWORD"] = "admin123"

        with self.assertRaises(RuntimeError):
            bootstrap_service.garantir_admin_inicial(SimpleNamespace())


if __name__ == "__main__":
    unittest.main()
