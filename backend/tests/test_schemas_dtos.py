import unittest
from datetime import UTC, date, datetime

from pydantic import ValidationError

from app.schemas.auth import AuthUserOut, TokenOut
from app.schemas.common import MensagemOut
from app.schemas.documento import DocumentoOut
from app.schemas.ferias import DisponibilidadeOut, FeriasOut, MinhasFeriasOut
from app.schemas.importacao import ImportacaoOut
from app.schemas.relatorio import DashboardOut, LogDetalhadoOut, RelatorioColaboradoresOut
from app.schemas.user import AniversarianteOut, UserCreate, UserResponse
from app.schemas.cargo import CargoCreate


class SchemasDtoTests(unittest.TestCase):
    def test_cargo_normaliza_espacos_antes_de_validar(self):
        self.assertEqual(CargoCreate(nome="  Analista   de BI  ").nome, "Analista de BI")
        with self.assertRaises(ValueError):
            CargoCreate(nome="   ")

    def test_user_create_aceita_novos_dados_do_colaborador(self):
        user = UserCreate(
            nome="Gabriel",
            email="gabriel@sistema.com",
            senha="segura123",
            role="user",
            dias_totais=30,
            saldo_inicial_dias=15,
            proxima_concessao_ferias=date(2027, 1, 10),
            departamento_id=1,
            data_admissao=date(2025, 1, 10),
            data_aniversario=date(1990, 5, 20),
            cor="#3b82f6",
            telefone="(11) 99999-9999",
            telefone_emergencia="(11) 98888-8888",
            telefone_emergencia_2="(11) 97777-7777",
            endereco={
                "logradouro": "Rua Exemplo",
                "numero": "10",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "cep": "01000-000",
            },
            dados_bancarios={
                "banco": "Banco Exemplo",
                "agencia": "1234",
                "conta": "56789-0",
                "cpf_titular": "529.982.247-25",
                "nome_titular": "Gabriel",
                "chave_pix": "gabriel@sistema.com",
            },
            cargo="Desenvolvedor",
            cpf="529.982.247-25",
        )

        self.assertEqual(user.cargo, "Desenvolvedor")
        self.assertEqual(user.telefone_emergencia_2, "(11) 97777-7777")
        self.assertEqual(user.endereco.numero, "10")
        self.assertEqual(user.dados_bancarios.agencia, "1234")
        self.assertEqual(user.cpf, "529.982.247-25")
        self.assertEqual(user.saldo_inicial_dias, 15)

    def test_user_create_rejeita_cadastro_incompleto(self):
        with self.assertRaises(ValidationError):
            UserCreate(nome="Gabriel", email="gabriel@sistema.com", senha="segura123")

    def test_user_create_rejeita_cpf_invalido_do_titular_bancario(self):
        dados = {
            "nome": "Gabriel",
            "email": "gabriel@sistema.com",
            "senha": "segura123",
            "role": "user",
            "dias_totais": 30,
            "departamento_id": 1,
            "data_admissao": date(2025, 1, 10),
            "data_aniversario": date(1990, 5, 20),
            "cor": "#3b82f6",
            "telefone": "(11) 99999-9999",
            "telefone_emergencia": "(11) 98888-8888",
            "telefone_emergencia_2": "(11) 97777-7777",
            "endereco": {"logradouro": "Rua A", "numero": "1", "bairro": "Centro", "cidade": "SP", "cep": "01000-000"},
            "dados_bancarios": {"banco": "Banco", "agencia": "1", "conta": "2", "cpf_titular": "111.111.111-11", "nome_titular": "Gabriel", "chave_pix": "pix"},
            "cargo": "Desenvolvedor",
            "cpf": "529.982.247-25",
        }
        with self.assertRaises(ValidationError):
            UserCreate(**dados)

    def test_user_create_exige_cpf_mesmo_com_demais_campos_validos(self):
        dados = {
            "nome": "Gabriel",
            "email": "gabriel@sistema.com",
            "senha": "segura123",
            "role": "user",
            "dias_totais": 30,
            "departamento_id": 1,
            "data_admissao": date(2025, 1, 10),
            "data_aniversario": date(1990, 5, 20),
            "cor": "#3b82f6",
            "telefone": "(11) 99999-9999",
            "telefone_emergencia": "(11) 98888-8888",
            "telefone_emergencia_2": "(11) 97777-7777",
            "endereco": {
                "logradouro": "Rua Exemplo",
                "numero": "10",
                "bairro": "Centro",
                "cidade": "Sao Paulo",
                "cep": "01000-000",
            },
            "dados_bancarios": {
                "banco": "Banco Exemplo",
                "agencia": "1234",
                "conta": "56789-0",
                "cpf_titular": "529.982.247-25",
                "nome_titular": "Gabriel",
                "chave_pix": "gabriel@sistema.com",
            },
            "cargo": "Desenvolvedor",
        }

        with self.assertRaises(ValidationError) as exc:
            UserCreate(**dados)

        self.assertIn("cpf", str(exc.exception))

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
            criado_por_id=2,
            criado_por_nome="Gabriel",
            destinatario_nome="Gabriel",
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

    def test_relatorio_colaboradores_out_aceita_shape_do_csv(self):
        hoje = datetime.now(UTC).date()
        response = RelatorioColaboradoresOut(
            colaboradores=[
                {
                    "id": 1,
                    "nome": "Gabriel",
                    "email": "gabriel@sistema.com",
                    "departamento": {"id": 1, "nome": "RH"},
                    "dias_totais": 30,
                    "dias_usados": 5,
                    "dias_restantes": 25,
                    "ciclo_inicio": hoje,
                    "ciclo_fim": hoje,
                    "ferias": [
                        {
                            "id": 1,
                            "data_inicio": hoje,
                            "data_fim": hoje,
                            "dias_usados": 1,
                            "status": "aprovada",
                            "ferias_acordo": False,
                        }
                    ],
                    "ferias_acordo": [],
                    "ferias_pendentes": [],
                }
            ]
        )

        self.assertEqual(response.colaboradores[0].ferias[0].status, "aprovada")

    def test_dashboard_out_aceita_shape_do_dashboard(self):
        hoje = datetime.now(UTC).date()
        response = DashboardOut(
            total_colaboradores=1,
            total_ferias_aprovadas=2,
            total_ferias_pendentes=3,
            total_ferias_rejeitadas=4,
            total_autorizacoes_equipamentos_pendentes=6,
            total_departamentos=5,
            pessoas_em_ferias=[
                {
                    "id": 1,
                    "nome": "Gabriel",
                    "cor": None,
                    "data_inicio": hoje,
                    "data_fim": hoje,
                    "dias_restantes": 1,
                }
            ],
            proximas_ferias=[],
            alertas_contabilidade=[],
        )

        self.assertEqual(response.total_departamentos, 5)

    def test_log_detalhado_out_aceita_usuario_sistema(self):
        log = LogDetalhadoOut(
            id=1,
            user_id=None,
            nome_usuario="Sistema",
            email_usuario=None,
            acao="TESTE",
            detalhes=None,
            criado_em=datetime.now(UTC),
        )

        self.assertEqual(log.nome_usuario, "Sistema")

    def test_importacao_out_aceita_resultado_da_importacao(self):
        response = ImportacaoOut(
            inseridos=1,
            erros=[],
            mensagem="1 registro(s) importado(s) com sucesso. 0 erro(s).",
        )

        self.assertEqual(response.inseridos, 1)

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
