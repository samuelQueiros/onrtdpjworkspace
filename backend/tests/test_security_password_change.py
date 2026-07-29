import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request

from app.core import security


class FakeQuery:
    def __init__(self, user):
        self.user = user

    def filter(self, *_args):
        return self

    def first(self):
        return self.user


class FakeDb:
    def __init__(self, user):
        self.user = user

    def query(self, _model):
        return FakeQuery(self.user)


def request_para(path: str) -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        }
    )


class SecurityPasswordChangeTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(
            id=7,
            ativo=True,
            token_version=2,
            must_change_password=True,
        )
        self.payload = {"sub": "7", "token_version": 2}

    def test_bloqueia_rotas_normais_ate_trocar_senha(self):
        with patch("app.core.security.jwt.decode", return_value=self.payload):
            with self.assertRaises(HTTPException) as exc:
                security.get_current_user(
                    request_para("/users"),
                    token="token",
                    db=FakeDb(self.user),
                )

        self.assertEqual(exc.exception.status_code, 403)
        self.assertEqual(exc.exception.detail, "PASSWORD_CHANGE_REQUIRED")

    def test_permite_consultar_sessao_e_trocar_senha(self):
        with patch("app.core.security.jwt.decode", return_value=self.payload):
            self.assertIs(
                security.get_current_user(
                    request_para("/auth/me"),
                    token="token",
                    db=FakeDb(self.user),
                ),
                self.user,
            )
            self.assertIs(
                security.get_current_user(
                    request_para("/me/configuracoes"),
                    token="token",
                    db=FakeDb(self.user),
                ),
                self.user,
            )

    def test_sub_nao_numerico_retorna_401(self):
        with patch(
            "app.core.security.jwt.decode",
            return_value={"sub": "nao-numerico", "token_version": 2},
        ):
            with self.assertRaises(HTTPException) as exc:
                security.get_current_user(
                    request_para("/auth/me"),
                    token="token",
                    db=FakeDb(self.user),
                )

        self.assertEqual(exc.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
