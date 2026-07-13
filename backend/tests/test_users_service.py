import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.schemas.user import UserConfigUpdate
from app.services import users_service


class UsersServiceTests(unittest.TestCase):
    def test_validar_email_disponivel_rejeita_email_existente(self):
        with patch("app.services.users_service.users_repository.obter_usuario_por_email", return_value=SimpleNamespace(id=1)):
            with self.assertRaises(HTTPException) as exc:
                users_service.validar_email_disponivel(SimpleNamespace(), "admin@sistema.com")

        self.assertEqual(exc.exception.status_code, 400)

    def test_validar_departamento_rejeita_departamento_inexistente(self):
        with patch("app.services.users_service.users_repository.obter_departamento_por_id", return_value=None):
            with self.assertRaises(HTTPException) as exc:
                users_service.validar_departamento(SimpleNamespace(), 99)

        self.assertEqual(exc.exception.status_code, 404)

    def test_excluir_usuario_bloqueia_excluir_propria_conta(self):
        current_user = SimpleNamespace(id=1)

        with self.assertRaises(HTTPException) as exc:
            users_service.desativar_usuario(SimpleNamespace(), 1, current_user)

        self.assertEqual(exc.exception.status_code, 400)

    def test_listar_aniversariantes_retorna_apenas_mes_atual(self):
        hoje = date.today()
        usuarios = [
            SimpleNamespace(nome="Pessoa A", data_aniversario=date(1990, hoje.month, 10)),
            SimpleNamespace(nome="Pessoa B", data_aniversario=date(1990, 1 if hoje.month != 1 else 2, 10)),
        ]

        with patch("app.services.users_service.users_repository.listar_usuarios_com_aniversario", return_value=usuarios):
            response = users_service.listar_aniversariantes(SimpleNamespace())

        self.assertEqual(response, [{"nome": "Pessoa A", "data_aniversario": usuarios[0].data_aniversario}])

    def test_atualizar_configuracoes_exige_senha_atual_para_trocar_senha(self):
        current_user = SimpleNamespace(id=1, senha_hash="hash")
        payload = UserConfigUpdate(nova_senha="nova-senha")

        with self.assertRaises(HTTPException) as exc:
            users_service.atualizar_configuracoes(SimpleNamespace(), payload, current_user)

        self.assertEqual(exc.exception.status_code, 400)

    def test_atualizar_configuracoes_rejeita_senha_atual_incorreta(self):
        current_user = SimpleNamespace(id=1, senha_hash="hash")
        payload = UserConfigUpdate(senha_atual="errada", nova_senha="nova-senha")

        with patch("app.services.users_service.verificar_senha", return_value=False):
            with self.assertRaises(HTTPException) as exc:
                users_service.atualizar_configuracoes(SimpleNamespace(), payload, current_user)

        self.assertEqual(exc.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
