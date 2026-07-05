import unittest
from datetime import UTC, datetime

from app.schemas.auth import AuthUserOut, TokenOut
from app.schemas.documento import DocumentoOut, MensagemOut
from app.schemas.user import AniversarianteOut, UserResponse


class SchemasDtoTests(unittest.TestCase):
    def test_token_out_aceita_formato_do_login(self):
        token = TokenOut(
            access_token="token",
            token_type="bearer",
            user={
                "id": 1,
                "nome": "Admin",
                "email": "admin@sistema.com",
                "role": "admin",
                "dias_totais": 30,
                "dias_restantes": 20,
                "departamento": None,
                "data_admissao": None,
                "data_aniversario": None,
            },
        )

        self.assertEqual(token.user.email, "admin@sistema.com")

    def test_auth_user_out_aceita_departamento(self):
        user = AuthUserOut(
            id=1,
            nome="Admin",
            email="admin@sistema.com",
            role="admin",
            dias_totais=30,
            dias_restantes=20,
            departamento={"id": 2, "nome": "RH"},
            data_admissao="2026-01-01",
            data_aniversario=None,
        )

        self.assertEqual(user.departamento.nome, "RH")

    def test_documento_out_aceita_formato_das_rotas(self):
        documento = DocumentoOut(
            id=1,
            user_id=2,
            tipo="atestado",
            nome_arquivo="arquivo.pdf",
            mime_type="application/pdf",
            tamanho=123,
            criado_por_nome="Gabriel",
            criado_em=datetime.now(UTC),
        )

        self.assertEqual(documento.mime_type, "application/pdf")

    def test_mensagem_out_aceita_detail(self):
        mensagem = MensagemOut(detail="Documento excluido com sucesso")

        self.assertEqual(mensagem.detail, "Documento excluido com sucesso")

    def test_user_response_aceita_formato_das_rotas_de_usuarios(self):
        user = UserResponse(
            id=1,
            nome="Admin",
            email="admin@sistema.com",
            role="admin",
            dias_totais=30,
            dias_restantes=20,
            departamento_id=2,
            departamento={"id": 2, "nome": "RH"},
            data_admissao=None,
            data_aniversario=None,
            cor="#ffffff",
            criado_em=datetime.now(UTC),
        )

        self.assertEqual(user.departamento.nome, "RH")

    def test_aniversariante_out_aceita_data(self):
        aniversariante = AniversarianteOut(nome="Gabriel", data_aniversario=datetime.now(UTC).date())

        self.assertEqual(aniversariante.nome, "Gabriel")


if __name__ == "__main__":
    unittest.main()
