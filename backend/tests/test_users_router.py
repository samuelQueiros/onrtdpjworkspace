import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import Response

from app.routers import users
from app.schemas.user import UserConfigUpdate


class UsersRouterTests(unittest.TestCase):
    def test_troca_de_senha_renova_cookie_da_sessao_atual(self):
        payload = UserConfigUpdate(
            senha_atual="senha-antiga",
            nova_senha="SenhaNova1!",
        )
        response = Response()
        current_user = SimpleNamespace(
            id=7,
            role="user",
            nome="Usuario",
            token_version=3,
        )

        with (
            patch(
                "app.routers.users.users_service.atualizar_configuracoes",
                return_value={"id": 7},
            ),
            patch("app.routers.users.criar_token", return_value="token-renovado") as criar,
        ):
            resultado = users.atualizar_configuracoes(
                payload,
                response,
                SimpleNamespace(),
                current_user,
            )

        self.assertEqual(resultado, {"id": 7})
        self.assertIn("access_token=token-renovado", response.headers["set-cookie"])
        self.assertIn("HttpOnly", response.headers["set-cookie"])
        criar.assert_called_once()
        self.assertEqual(criar.call_args.args[0]["token_version"], 3)

    def test_atualizacao_sem_senha_nao_renova_cookie(self):
        payload = UserConfigUpdate(telefone="(11) 99999-0000")
        response = Response()
        current_user = SimpleNamespace(
            id=7,
            role="user",
            nome="Usuario",
            token_version=2,
        )

        with patch(
            "app.routers.users.users_service.atualizar_configuracoes",
            return_value={"id": 7},
        ):
            users.atualizar_configuracoes(
                payload,
                response,
                SimpleNamespace(),
                current_user,
            )

        self.assertNotIn("set-cookie", response.headers)


if __name__ == "__main__":
    unittest.main()
