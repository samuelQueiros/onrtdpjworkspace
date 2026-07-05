import os
import unittest

from app.core.crypto import (
    CREDENTIAL_PREFIX,
    criptografar_credencial,
    descriptografar_credencial,
)
from app.schemas.credencial import CredencialCreate
from app.services.credenciais_service import criar_credencial, formatar_credencial


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

    def test_producao_exige_chave_de_criptografia(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ.pop("SECRET_KEY", None)
        os.environ.pop("CREDENTIALS_ENCRYPTION_KEY", None)

        with self.assertRaises(RuntimeError):
            criptografar_credencial("senha")


if __name__ == "__main__":
    unittest.main()
