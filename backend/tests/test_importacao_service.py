from datetime import date, datetime
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.services import importacao_service


class ImportacaoServiceTests(unittest.TestCase):
    def test_parse_date_aceita_formatos_suportados(self):
        self.assertEqual(importacao_service.parse_date("2026-07-05"), date(2026, 7, 5))
        self.assertEqual(importacao_service.parse_date("05/07/2026"), date(2026, 7, 5))
        self.assertEqual(importacao_service.parse_date("05-07-2026"), date(2026, 7, 5))

    def test_validar_extensao_planilha_rejeita_extensao_invalida(self):
        with self.assertRaises(HTTPException) as exc:
            importacao_service.validar_extensao_planilha("arquivo.csv")

        self.assertEqual(exc.exception.status_code, 400)

    def test_importar_ferias_insere_registro_e_log(self):
        rows = [
            ("email", "data_inicio", "data_fim", "ferias_acordo"),
            ("gabriel@sistema.com", "2027-07-05", "2027-07-09", False),
        ]
        user = SimpleNamespace(id=2)
        current_user = SimpleNamespace(id=1)

        with (
            patch("app.services.importacao_service.carregar_linhas_planilha", return_value=rows),
            patch("app.services.importacao_service.importacao_repository.obter_usuario_por_email", return_value=user),
            patch("app.services.importacao_service.importacao_repository.existe_ferias_periodo", return_value=False),
            patch("app.services.importacao_service.ferias_service.bloquear_regras_ferias"),
            patch("app.services.importacao_service.ferias_service.verificar_regras_data"),
            patch("app.services.importacao_service.ferias_service.verificar_bloqueio_datas"),
            patch("app.services.importacao_service.ferias_service.verificar_sobreposicao_departamento", return_value=False),
            patch("app.services.importacao_service.ferias_service.calcular_saldo", return_value=30),
            patch("app.services.importacao_service.importacao_repository.adicionar_ferias") as adicionar_ferias,
            patch("app.services.importacao_service.importacao_repository.adicionar_log") as adicionar_log,
            patch("app.services.importacao_service.importacao_repository.commit") as commit,
        ):
            response = importacao_service.importar_ferias(SimpleNamespace(), "ferias.xlsx", b"conteudo", current_user)

        self.assertEqual(response["inseridos"], 1)
        adicionar_ferias.assert_called_once()
        adicionar_log.assert_called_once()
        commit.assert_called_once()

    def test_importar_ferias_registra_erro_para_usuario_inexistente(self):
        rows = [("email", "data_inicio", "data_fim"), ("naoexiste@sistema.com", "2027-07-05", "2027-07-09")]

        with (
            patch("app.services.importacao_service.carregar_linhas_planilha", return_value=rows),
            patch("app.services.importacao_service.importacao_repository.obter_usuario_por_email", return_value=None),
            patch("app.services.importacao_service.importacao_repository.commit") as commit,
        ):
            response = importacao_service.importar_ferias(SimpleNamespace(), "ferias.xlsx", b"conteudo", SimpleNamespace(id=1))

        self.assertEqual(response["inseridos"], 0)
        self.assertEqual(len(response["erros"]), 1)
        commit.assert_not_called()

    def test_importar_logs_insere_log_com_data_parseada(self):
        rows = [("data", "acao", "detalhes"), ("05/07/2026 10:30", "ACAO", "Detalhe")]

        with (
            patch("app.services.importacao_service.carregar_linhas_planilha", return_value=rows),
            patch("app.services.importacao_service.importacao_repository.adicionar_log") as adicionar_log,
            patch("app.services.importacao_service.importacao_repository.commit") as commit,
        ):
            response = importacao_service.importar_logs(SimpleNamespace(), "logs.xlsx", b"conteudo", SimpleNamespace(id=1))

        self.assertEqual(response["inseridos"], 1)
        log = adicionar_log.call_args.args[1]
        self.assertEqual(log.criado_em, datetime(2026, 7, 5, 10, 30))
        commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
