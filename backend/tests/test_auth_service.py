import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.services import auth_service


class AuthServiceTests(unittest.TestCase):
    def test_autenticar_usuario_retorna_token_e_usuario_formatado(self):
        user = SimpleNamespace(
            id=1,
            nome="Admin",
            email="admin@sistema.com",
            role="admin",
            senha_hash="hash",
            token_version=0,
            dias_totais=30,
            departamento_id=None,
            data_admissao=None,
            data_aniversario=None,
        )

        with (
            patch("app.services.auth_service.auth_repository.obter_usuario_por_email", return_value=user),
            patch("app.services.auth_service.verificar_senha", return_value=True),
            patch("app.services.auth_service.criar_token", return_value="token"),
            patch("app.services.auth_service.calcular_dias_restantes", return_value=20),
        ):
            response = auth_service.autenticar_usuario(SimpleNamespace(), "admin@sistema.com", "senha")

        self.assertEqual(response["access_token"], "token")
        self.assertEqual(response["token_type"], "bearer")
        self.assertEqual(response["user"]["id"], 1)
        self.assertEqual(response["user"]["dias_restantes"], 20)

    def test_autenticar_usuario_rejeita_email_inexistente(self):
        with patch("app.services.auth_service.auth_repository.obter_usuario_por_email", return_value=None):
            with self.assertRaises(HTTPException) as exc:
                auth_service.autenticar_usuario(SimpleNamespace(), "naoexiste@sistema.com", "senha")

        self.assertEqual(exc.exception.status_code, 401)

    def test_autenticar_usuario_rejeita_senha_incorreta(self):
        user = SimpleNamespace(senha_hash="hash")

        with (
            patch("app.services.auth_service.auth_repository.obter_usuario_por_email", return_value=user),
            patch("app.services.auth_service.verificar_senha", return_value=False),
        ):
            with self.assertRaises(HTTPException) as exc:
                auth_service.autenticar_usuario(SimpleNamespace(), "admin@sistema.com", "senha-errada")

        self.assertEqual(exc.exception.status_code, 401)

    def test_formatar_usuario_autenticado_inclui_departamento(self):
        user = SimpleNamespace(
            id=1,
            nome="Admin",
            email="admin@sistema.com",
            role="admin",
            dias_totais=30,
            departamento_id=10,
            data_admissao=None,
            data_aniversario=None,
        )
        departamento = SimpleNamespace(id=10, nome="RH")

        with (
            patch("app.services.auth_service.auth_repository.obter_departamento_por_id", return_value=departamento),
            patch("app.services.auth_service.calcular_dias_restantes", return_value=30),
        ):
            response = auth_service.formatar_usuario_autenticado(user, SimpleNamespace())

        self.assertEqual(response["departamento"], {"id": 10, "nome": "RH"})


if __name__ == "__main__":
    unittest.main()
