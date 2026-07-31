import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from app.core.crypto import (
    CREDENTIAL_PREFIX,
    SENSITIVE_PREFIX,
    criptografar_credencial,
    criptografar_dado_sensivel,
    descriptografar_credencial,
    descriptografar_dado_sensivel,
)
from app.schemas.credencial import CredencialCreate
from app.services.credenciais_service import (
    criar_credencial,
    formatar_credencial,
    minhas_credenciais,
    revelar_credencial,
)


class FakeDb:
    def __init__(self):
        self.saved = None

    def add(self, obj):
        self.saved = obj

    def commit(self):
        pass

    def refresh(self, obj):
        obj.id = 1
        obj.usuarios = []


class CredenciaisCryptoTests(unittest.TestCase):
    def setUp(self):
        self.old_environment = os.environ.get("ENVIRONMENT")
        self.old_secret_key = os.environ.get("SECRET_KEY")
        self.old_credentials_key = os.environ.get("CREDENTIALS_ENCRYPTION_KEY")
        os.environ["ENVIRONMENT"] = "development"
        os.environ["CREDENTIALS_ENCRYPTION_KEY"] = "chave-de-teste-com-tamanho-suficiente"

    def tearDown(self):
        self._restore_env("ENVIRONMENT", self.old_environment)
        self._restore_env("SECRET_KEY", self.old_secret_key)
        self._restore_env("CREDENTIALS_ENCRYPTION_KEY", self.old_credentials_key)

    def _restore_env(self, key, value):
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    def test_criptografa_e_descriptografa_credencial(self):
        senha = "senha-super-secreta"

        senha_criptografada = criptografar_credencial(senha)

        self.assertNotEqual(senha_criptografada, senha)
        self.assertTrue(senha_criptografada.startswith(CREDENTIAL_PREFIX))
        self.assertEqual(descriptografar_credencial(senha_criptografada), senha)

    def test_criar_credencial_nao_salva_senha_em_texto_puro(self):
        db = FakeDb()
        payload = CredencialCreate(
            descricao="Sistema interno",
            email="acesso@sistema.com",
            senha="senha-original",
        )

        response = criar_credencial(payload=payload, db=db)

        self.assertNotEqual(db.saved.senha, "senha-original")
        self.assertTrue(db.saved.senha.startswith(CREDENTIAL_PREFIX))
        self.assertNotIn("senha", response)

    def test_criptografa_e_descriptografa_dado_sensivel(self):
        valor = "Banco 001, conta 123"
        protegido = criptografar_dado_sensivel(valor)
        self.assertTrue(protegido.startswith(SENSITIVE_PREFIX))
        self.assertNotEqual(protegido, valor)
        self.assertEqual(descriptografar_dado_sensivel(protegido), valor)

    def test_fmt_credencial_descriptografa_somente_quando_solicitado(self):
        db = FakeDb()
        payload = CredencialCreate(
            descricao="Sistema interno",
            email="acesso@sistema.com",
            senha="senha-original",
        )
        criar_credencial(payload=payload, db=db)

        sem_senha = formatar_credencial(db.saved)
        com_senha = formatar_credencial(db.saved, incluir_senha=True)

        self.assertNotIn("senha", sem_senha)
        self.assertEqual(com_senha["senha"], "senha-original")

    def test_listagem_compartilhada_nao_descriptografa_senhas(self):
        credencial = SimpleNamespace(
            id=1,
            descricao="Sistema interno",
            email="acesso@sistema.com",
            criado_em=None,
            atualizado_em=None,
            usuarios=[],
            senha="nao-deve-ser-lida",
        )
        with patch(
            "app.services.credenciais_service.credenciais_repository.listar_credenciais_por_usuario",
            return_value=[credencial],
        ):
            resultado = minhas_credenciais(FakeDb(), 7)

        self.assertNotIn("senha", resultado[0])

    def test_revelacao_exige_senha_atual_e_grava_auditoria(self):
        db = FakeDb()
        credencial = SimpleNamespace(id=3, senha=criptografar_credencial("segredo"))
        usuario = SimpleNamespace(id=7, role="user", senha_hash="hash")
        with (
            patch("app.services.credenciais_service.buscar_credencial", return_value=credencial),
            patch(
                "app.services.credenciais_service.credenciais_repository.usuario_tem_acesso",
                return_value=True,
            ),
            patch("app.services.credenciais_service.verificar_senha", return_value=True),
        ):
            resultado = revelar_credencial(db, 3, "senha-atual", usuario)

        self.assertEqual(resultado, {"id": 3, "senha": "segredo"})
        self.assertEqual(db.saved.acao, "CREDENCIAL_REVELADA")

    def test_revelacao_oculta_credencial_sem_permissao(self):
        db = FakeDb()
        credencial = SimpleNamespace(id=3, senha=criptografar_credencial("segredo"))
        usuario = SimpleNamespace(id=7, role="user", senha_hash="hash")
        with (
            patch("app.services.credenciais_service.buscar_credencial", return_value=credencial),
            patch(
                "app.services.credenciais_service.credenciais_repository.usuario_tem_acesso",
                return_value=False,
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                revelar_credencial(db, 3, "senha-atual", usuario)

        self.assertEqual(exc.exception.status_code, 404)

    def test_producao_exige_chave_de_criptografia(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ.pop("SECRET_KEY", None)
        os.environ.pop("CREDENTIALS_ENCRYPTION_KEY", None)

        with self.assertRaises(RuntimeError):
            criptografar_credencial("senha")


if __name__ == "__main__":
    unittest.main()
