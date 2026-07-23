import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.schemas.user import DadosBancarios, UserConfigUpdate
from app.services import users_service


class UsersServiceTests(unittest.TestCase):
    def test_preparar_cpf_normaliza_hash_e_criptografia(self):
        db = SimpleNamespace()
        with (
            patch("app.services.users_service.hash_dado_sensivel", return_value="hash-cpf") as hash_mock,
            patch("app.services.users_service.criptografar_dado_sensivel", return_value="cpf-criptografado") as crypto_mock,
            patch("app.services.users_service.users_repository.obter_usuario_por_cpf_hash", return_value=None) as repo_mock,
        ):
            resultado = users_service.preparar_cpf(db, "529.982.247-25")

        self.assertEqual(resultado, ("cpf-criptografado", "hash-cpf"))
        hash_mock.assert_called_once_with("52998224725")
        crypto_mock.assert_called_once_with("52998224725")
        repo_mock.assert_called_once_with(db, "hash-cpf", None)

    def test_preparar_cpf_rejeita_cpf_duplicado(self):
        with (
            patch("app.services.users_service.hash_dado_sensivel", return_value="hash-cpf"),
            patch(
                "app.services.users_service.users_repository.obter_usuario_por_cpf_hash",
                return_value=SimpleNamespace(id=9),
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                users_service.preparar_cpf(SimpleNamespace(), "529.982.247-25", excluir_user_id=2)

        self.assertEqual(exc.exception.status_code, 400)
        self.assertEqual(exc.exception.detail, "CPF ja cadastrado para outro colaborador")

    def test_preparar_cpf_rejeita_cpf_invalido_antes_de_consultar_banco(self):
        with patch("app.services.users_service.users_repository.obter_usuario_por_cpf_hash") as repo_mock:
            with self.assertRaises(HTTPException) as exc:
                users_service.preparar_cpf(SimpleNamespace(), "111.111.111-11")

        self.assertEqual(exc.exception.status_code, 400)
        repo_mock.assert_not_called()

    def test_formatar_usuario_expoe_apenas_cpf_mascarado(self):
        user = SimpleNamespace(
            id=1,
            nome="Gabriel",
            email="gabriel@sistema.com",
            role="user",
            dias_totais=30,
            departamento_id=None,
            departamento=None,
            data_admissao=None,
            data_aniversario=None,
            cor=None,
            telefone="(61) 99999-9999",
            cpf_criptografado="cpf-criptografado",
            cargo=None,
            ativo=True,
            saldo_manual_dias=None,
            criado_em=None,
        )
        with patch("app.services.users_service.descriptografar_dado_sensivel", return_value="52998224725"):
            resultado = users_service.formatar_usuario(user, SimpleNamespace(), dias_restantes=30, dias_usados_total=0)

        self.assertEqual(resultado["cpf_mascarado"], "***.***.***-25")
        self.assertNotIn("cpf", resultado)

    def test_consulta_sensivel_expoe_cpf_formatado_e_registra_auditoria(self):
        user = SimpleNamespace(
            cpf_criptografado="cpf-criptografado",
            telefone_emergencia="(61) 99999-9999",
            telefone_emergencia_2="(61) 98888-8888",
            endereco=None,
            dados_bancarios=None,
        )

        class FakeDb:
            def __init__(self):
                self.added = []
                self.committed = False

            def add(self, obj):
                self.added.append(obj)

            def commit(self):
                self.committed = True

        db = FakeDb()
        with (
            patch("app.services.users_service.buscar_usuario", return_value=user),
            patch("app.services.users_service.descriptografar_dado_sensivel", return_value="52998224725"),
        ):
            resultado = users_service.consultar_dados_sensiveis(
                db, 8, SimpleNamespace(id=1, role="admin")
            )

        self.assertEqual(resultado["cpf"], "529.982.247-25")
        self.assertTrue(db.committed)
        self.assertEqual(db.added[0].acao, "CPF_COMPLETO_E_DADOS_SENSIVEIS_CONSULTADOS")

    def test_endereco_estruturado_e_formato_antigo(self):
        endereco = users_service.Endereco(
            logradouro="Rua Exemplo", numero="10", bairro="Centro", cidade="São Paulo", cep="01000-000"
        )
        valor = users_service._serializar_endereco(endereco)
        restaurado = users_service._desserializar_endereco(valor)
        legado = users_service._desserializar_endereco("Rua Antiga, 25")

        self.assertTrue(valor.startswith("sensitive:"))
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

    def test_listar_usuarios_calcula_saldo_cumulativo_em_lote(self):
        hoje = date.today()
        data_admissao = date(hoje.year - 2, 1, 1)
        user = SimpleNamespace(
            id=1,
            nome="Gabriel",
            email="gabriel@sistema.com",
            role="user",
            dias_totais=30,
            departamento_id=None,
            departamento=None,
            data_admissao=data_admissao,
            data_aniversario=None,
            cor=None,
            telefone=None,
            cpf_criptografado=None,
            cargo=None,
            ativo=True,
            saldo_manual_dias=None,
            criado_em=None,
        )
        ferias_fake = SimpleNamespace(user_id=1, dias_usados=10)

        with (
            patch("app.services.users_service.users_repository.listar_usuarios", return_value=[user]),
            patch("app.services.users_service.users_repository.listar_ferias_para_saldos", return_value=[ferias_fake]),
        ):
            resultado = users_service.listar_usuarios(SimpleNamespace())

        self.assertEqual(resultado[0]["dias_restantes"], 50)
        self.assertEqual(resultado[0]["dias_usados_total"], 10)

    def test_listar_usuarios_respeita_override_manual_de_saldo(self):
        hoje = date.today()
        data_admissao = date(hoje.year - 2, 1, 1)
        user = SimpleNamespace(
            id=1,
            nome="Gabriel",
            email="gabriel@sistema.com",
            role="user",
            dias_totais=30,
            departamento_id=None,
            departamento=None,
            data_admissao=data_admissao,
            data_aniversario=None,
            cor=None,
            telefone=None,
            cpf_criptografado=None,
            cargo=None,
            ativo=True,
            saldo_manual_dias=80,
            criado_em=None,
        )
        ferias_fake = SimpleNamespace(user_id=1, dias_usados=10)

        with (
            patch("app.services.users_service.users_repository.listar_usuarios", return_value=[user]),
            patch("app.services.users_service.users_repository.listar_ferias_para_saldos", return_value=[ferias_fake]),
        ):
            resultado = users_service.listar_usuarios(SimpleNamespace())

        self.assertEqual(resultado[0]["dias_restantes"], 80)

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

    def test_atualizar_configuracoes_atualiza_telefones_do_proprio_perfil(self):
        current_user = SimpleNamespace(
            id=1,
            senha_hash="hash",
            nome="Gabriel",
            email="gabriel@sistema.com",
            telefone=None,
            telefone_emergencia=None,
            telefone_emergencia_2=None,
        )
        payload = UserConfigUpdate(
            telefone="(61) 99999-0000",
            telefone_emergencia="(61) 98888-0000",
            telefone_emergencia_2="(61) 97777-0000",
        )

        with (
            patch("app.services.users_service.users_repository.salvar_usuario"),
            patch("app.services.users_service.formatar_usuario", return_value={"id": 1}),
        ):
            users_service.atualizar_configuracoes(SimpleNamespace(), payload, current_user)

        self.assertEqual(current_user.telefone, "(61) 99999-0000")
        self.assertEqual(current_user.telefone_emergencia, "(61) 98888-0000")
        self.assertEqual(current_user.telefone_emergencia_2, "(61) 97777-0000")

    def test_meu_perfil_combina_dados_basicos_e_sensiveis(self):
        user = SimpleNamespace(
            id=1,
            nome="Gabriel",
            email="gabriel@sistema.com",
            role="user",
            dias_totais=30,
            departamento_id=None,
            departamento=None,
            data_admissao=None,
            data_aniversario=None,
            cor="#123456",
            telefone="(61) 99999-9999",
            telefone_emergencia="(61) 98888-8888",
            telefone_emergencia_2=None,
            endereco=None,
            dados_bancarios=None,
            cpf_criptografado="cpf-criptografado",
            cargo=None,
            ativo=True,
            saldo_manual_dias=None,
            criado_em=None,
        )
        with (
            patch("app.services.users_service.calcular_dias_restantes", return_value=30),
            patch("app.services.users_service.calcular_dias_usados", return_value=0),
            patch("app.services.users_service.descriptografar_dado_sensivel", return_value="52998224725"),
        ):
            resultado = users_service.meu_perfil(SimpleNamespace(), user)

        self.assertEqual(resultado["cpf"], "529.982.247-25")
        self.assertEqual(resultado["telefone"], "(61) 99999-9999")
        self.assertEqual(resultado["telefone_emergencia"], "(61) 98888-8888")
        self.assertNotIn("cpf_mascarado", resultado)


if __name__ == "__main__":
    unittest.main()
