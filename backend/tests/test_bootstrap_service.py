import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.models.cargo import Cargo
from app.services import bootstrap_service


class BootstrapServiceTests(unittest.TestCase):
    def setUp(self):
        self.old_admin_email = os.environ.get("ADMIN_EMAIL")
        self.old_admin_password = os.environ.get("ADMIN_PASSWORD")
        self.old_admin_name = os.environ.get("ADMIN_NAME")
        self.old_environment = os.environ.get("ENVIRONMENT")
        self.old_create_test_users = os.environ.get("CREATE_TEST_USERS")
        self.old_test_user_password = os.environ.get("TEST_USER_PASSWORD")

    def tearDown(self):
        self._restore_env("ADMIN_EMAIL", self.old_admin_email)
        self._restore_env("ADMIN_PASSWORD", self.old_admin_password)
        self._restore_env("ADMIN_NAME", self.old_admin_name)
        self._restore_env("ENVIRONMENT", self.old_environment)
        self._restore_env("CREATE_TEST_USERS", self.old_create_test_users)
        self._restore_env("TEST_USER_PASSWORD", self.old_test_user_password)

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
            patch("app.services.ferias_service.registrar_saldo_inicial"),
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

    def test_seed_de_usuarios_fica_desabilitado_por_padrao(self):
        os.environ.pop("CREATE_TEST_USERS", None)

        db = MagicMock()

        self.assertEqual(bootstrap_service.garantir_usuarios_teste(db), 0)
        db.query.assert_not_called()

    def test_seed_exige_senha(self):
        os.environ["CREATE_TEST_USERS"] = "true"
        os.environ.pop("TEST_USER_PASSWORD", None)

        with self.assertRaises(RuntimeError):
            bootstrap_service.garantir_usuarios_teste(MagicMock())

    def test_seed_cria_tres_usuarios(self):
        os.environ["CREATE_TEST_USERS"] = "true"
        os.environ["TEST_USER_PASSWORD"] = "senha-de-teste"
        db = MagicMock()
        cargo = Cargo(id=1, nome="Desenvolvedor")
        resultados = [None, cargo, None, None, None, None, None, None]
        db.query.return_value.filter.return_value.first.side_effect = resultados

        with (
            patch("app.services.bootstrap_service.hash_senha", return_value="hash"),
            patch("app.services.bootstrap_service.hash_dado_sensivel", side_effect=lambda valor: f"hash-{valor}"),
            patch("app.services.bootstrap_service.criptografar_dado_sensivel", side_effect=lambda valor: f"enc-{valor}"),
        ):
            criados = bootstrap_service.garantir_usuarios_teste(db)

        self.assertEqual(criados, 3)
        usuarios = [
            item for chamada in db.add.call_args_list
            if (item := chamada.args[0]).__class__.__name__ == "User"
        ]
        self.assertEqual(
            [usuario.email for usuario in usuarios],
            [
                "ana.teste@sistema.local",
                "bruno.teste@sistema.local",
                "carla.teste@sistema.local",
            ],
        )
        self.assertTrue(all(usuario.senha_hash == "hash" for usuario in usuarios))
        db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
