import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.schemas.user import DadosBancarios, UserConfigUpdate
from app.services import users_service


class UsersServiceTests(unittest.TestCase):
    def test_endereco_estruturado_e_formato_antigo(self):
        endereco = users_service.Endereco(
            logradouro="Rua Exemplo", numero="10", bairro="Centro", cidade="São Paulo", cep="01000-000"
        )
        valor = users_service._serializar_endereco(endereco)
        restaurado = users_service._desserializar_endereco(valor)
        legado = users_service._desserializar_endereco("Rua Antiga, 25")

        self.assertEqual(restaurado["cidade"], "São Paulo")
        self.assertEqual(restaurado["cep"], "01000-000")
        self.assertEqual(legado["logradouro"], "Rua Antiga, 25")

    def test_dados_bancarios_estruturados_preservam_criptografia(self):
        dados = DadosBancarios(banco="Banco Exemplo", agencia="1234", chave_pix="pix@example.com")
        with (
            patch("app.services.users_service.criptografar_dado_sensivel", side_effect=lambda valor: f"enc:{valor}"),
            patch("app.services.users_service.descriptografar_dado_sensivel", side_effect=lambda valor: valor[4:]),
        ):
            valor = users_service._serializar_dados_bancarios(dados)
            restaurado = users_service._desserializar_dados_bancarios(valor)

        self.assertTrue(valor.startswith("enc:"))
        self.assertEqual(restaurado["banco"], "Banco Exemplo")
        self.assertEqual(restaurado["agencia"], "1234")
        self.assertEqual(restaurado["chave_pix"], "pix@example.com")

    def test_dados_bancarios_antigos_continuam_legiveis(self):
        with patch("app.services.users_service.descriptografar_dado_sensivel", return_value="Banco antigo, conta 123"):
            restaurado = users_service._desserializar_dados_bancarios("valor-criptografado")

        self.assertEqual(restaurado["banco"], "Banco antigo, conta 123")

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

    def test_desativar_bloqueia_ultimo_administrador(self):
        admin = SimpleNamespace(id=2, role="admin", ativo=True)
        with (
            patch("app.services.users_service.buscar_usuario", return_value=admin),
            patch("app.services.users_service.users_repository.contar_administradores_ativos", return_value=1),
        ):
            with self.assertRaises(HTTPException) as exc:
                users_service.desativar_usuario(SimpleNamespace(), 2, SimpleNamespace(id=1))
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
