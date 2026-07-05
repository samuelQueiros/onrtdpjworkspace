import unittest
from datetime import UTC, datetime

from app.schemas.auth import AuthUserOut, TokenOut
from app.schemas.common import MensagemOut
from app.schemas.documento import DocumentoOut
from app.schemas.ferias import DisponibilidadeOut, FeriasOut, MinhasFeriasOut
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

    def test_ferias_out_aceita_formato_das_rotas(self):
        ferias = FeriasOut(
            id=1,
            user_id=2,
            nome_usuario="Gabriel",
            cor_usuario="#ffffff",
            data_inicio=datetime.now(UTC).date(),
            data_fim=datetime.now(UTC).date(),
            dias_usados=1,
            status="pendente",
            ferias_acordo=False,
            motivo_rejeicao=None,
            criado_em=datetime.now(UTC),
            aprovado_por_id=None,
            aprovado_por_nome=None,
            aprovado_em=None,
            rejeitado_por_id=None,
            rejeitado_por_nome=None,
            rejeitado_em=None,
        )

        self.assertEqual(ferias.nome_usuario, "Gabriel")

    def test_minhas_ferias_out_aceita_saldo_e_ciclo(self):
        hoje = datetime.now(UTC).date()
        response = MinhasFeriasOut(ferias=[], saldo=30, ciclo_inicio=hoje, ciclo_fim=hoje)

        self.assertEqual(response.saldo, 30)

    def test_disponibilidade_out_aceita_listas_completas(self):
        hoje = datetime.now(UTC).date()
        response = DisponibilidadeOut(
            periodos_bloqueados=[{"data_inicio": hoje, "data_fim": hoje}],
            ferias_marcadas=[
                {
                    "id": 1,
                    "user_id": 2,
                    "nome": "Gabriel",
                    "cor": None,
                    "data_inicio": hoje,
                    "data_fim": hoje,
                    "dias_usados": 1,
                    "ferias_acordo": False,
                }
            ],
            bloqueios_manuais=[
                {
                    "id": 1,
                    "data_inicio": hoje,
                    "data_fim": hoje,
                    "motivo": "Recesso",
                    "tipo": "recesso",
                }
            ],
        )

        self.assertEqual(response.ferias_marcadas[0].nome, "Gabriel")

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
