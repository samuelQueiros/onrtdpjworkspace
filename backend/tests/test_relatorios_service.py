from datetime import date, datetime
from io import BytesIO
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from openpyxl import load_workbook

from app.services import relatorios_service


class RelatoriosServiceTests(unittest.TestCase):
    def test_exportar_logs_xlsx_preserva_acentos(self):
        usuario = SimpleNamespace(nome="João da Silva", email="joao@sistema.com")
        logs = [
            SimpleNamespace(
                criado_em=datetime(2026, 7, 27, 14, 30),
                acao="USUÁRIO_ATUALIZADO",
                usuario=usuario,
                detalhes="Alteração concluída com sucesso.",
            )
        ]
        with patch(
            "app.services.relatorios_service.relatorios_repository.listar_todos_logs",
            return_value=logs,
        ):
            conteudo = relatorios_service.exportar_logs_xlsx(SimpleNamespace())

        planilha = load_workbook(BytesIO(conteudo))["Logs"]
        self.assertEqual(planilha["B2"].value, "USUÁRIO_ATUALIZADO")
        self.assertEqual(planilha["C2"].value, "João da Silva")
        self.assertEqual(planilha["E2"].value, "Alteração concluída com sucesso.")
        self.assertEqual(planilha.freeze_panes, "A2")

    def test_relatorio_colaboradores_monta_shape_para_csv(self):
        user = SimpleNamespace(
            id=1,
            nome="Gabriel",
            email="gabriel@sistema.com",
            departamento_id=1,
            departamento=SimpleNamespace(id=1, nome="RH"),
            dias_totais=30,
            data_admissao=None,
        )
        ferias = SimpleNamespace(
            id=10,
            data_inicio=date(2026, 7, 6),
            data_fim=date(2026, 7, 10),
            dias_usados=5,
            status="aprovada",
            ferias_acordo=False,
        )

        with (
            patch("app.services.relatorios_service.relatorios_repository.listar_usuarios_ordenados", return_value=[user]),
            patch("app.services.relatorios_service.get_ciclo_atual", return_value=(date(2026, 1, 1), date(2026, 12, 31))),
            patch("app.services.relatorios_service.relatorios_repository.listar_ferias_aprovadas_ciclo", return_value=[ferias]),
            patch("app.services.relatorios_service.relatorios_repository.listar_ferias_acordo_aprovadas", return_value=[]),
            patch("app.services.relatorios_service.relatorios_repository.listar_ferias_pendentes_usuario", return_value=[]),
            patch("app.services.relatorios_service.calcular_saldo", return_value=25),
        ):
            response = relatorios_service.relatorio_colaboradores(SimpleNamespace())

        colaborador = response["colaboradores"][0]
        self.assertEqual(colaborador["nome"], "Gabriel")
        self.assertEqual(colaborador["dias_usados"], 5)
        self.assertEqual(colaborador["dias_restantes"], 25)
        self.assertEqual(colaborador["ferias"][0]["id"], 10)

    def test_dashboard_admin_monta_totais_e_listas(self):
        hoje = date.today()
        ferias = SimpleNamespace(
            id=1,
            user_id=2,
            usuario=SimpleNamespace(nome="Gabriel", cor="#ffffff"),
            data_inicio=hoje,
            data_fim=hoje,
            dias_usados=1,
        )

        with (
            patch("app.services.relatorios_service.relatorios_repository.contar_colaboradores", return_value=3),
            patch("app.services.relatorios_service.relatorios_repository.contar_ferias_por_status", side_effect=[4, 1, 2]),
            patch("app.services.relatorios_service.relatorios_repository.contar_autorizacoes_equipamentos_por_status", return_value=5),
            patch("app.services.relatorios_service.relatorios_repository.contar_departamentos", return_value=2),
            patch("app.services.relatorios_service.relatorios_repository.listar_ferias_em_andamento", return_value=[ferias]),
            patch("app.services.relatorios_service.relatorios_repository.listar_proximas_ferias", return_value=[ferias]),
            patch("app.services.relatorios_service.relatorios_repository.listar_alertas_contabilidade", return_value=[ferias]),
        ):
            response = relatorios_service.dashboard_admin(SimpleNamespace())

        self.assertEqual(response["total_colaboradores"], 3)
        self.assertEqual(response["total_ferias_aprovadas"], 4)
        self.assertEqual(response["total_autorizacoes_equipamentos_pendentes"], 5)
        self.assertEqual(response["pessoas_em_ferias"][0]["nome"], "Gabriel")
        self.assertEqual(response["alertas_contabilidade"][0]["ferias_id"], 1)

    def test_listar_logs_formata_usuario_sistema_quando_sem_usuario(self):
        log = SimpleNamespace(
            id=1,
            user_id=None,
            usuario=None,
            acao="TESTE",
            detalhes="Detalhe",
            criado_em=datetime(2026, 7, 5),
        )

        with (
            patch("app.services.relatorios_service.relatorios_repository.listar_logs", return_value=[log]),
            patch("app.services.relatorios_service.relatorios_repository.contar_logs", return_value=1),
        ):
            response = relatorios_service.listar_logs(SimpleNamespace())

        self.assertEqual(response["items"][0]["nome_usuario"], "Sistema")
        self.assertIsNone(response["items"][0]["email_usuario"])
        self.assertEqual(response["total"], 1)


if __name__ == "__main__":
    unittest.main()
