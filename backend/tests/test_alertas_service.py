from datetime import date, datetime
import unittest
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, patch

from app.services import alertas_service


class AlertasServiceTests(unittest.TestCase):
    def test_formatar_alerta_inclui_dados_das_ferias(self):
        ferias = SimpleNamespace(
            data_inicio=date(2026, 7, 10),
            data_fim=date(2026, 7, 20),
            dias_usados=11,
            usuario=SimpleNamespace(nome="Gabriel", cargo=SimpleNamespace(nome="Analista"), data_admissao=None),
        )
        alerta = SimpleNamespace(
            id=1,
            ferias_id=2,
            tipo="contabilidade_4dias",
            mensagem="Mensagem",
            lido=False,
            criado_em=datetime(2026, 7, 1),
            ferias=ferias,
        )

        response = alertas_service.formatar_alerta(alerta)

        self.assertEqual(response["ferias_usuario"], "Gabriel")
        self.assertEqual(response["ferias_data_inicio"], date(2026, 7, 10))
        self.assertEqual(response["cargo_usuario"], "Analista")
        self.assertEqual(response["retorno_trabalho"], date(2026, 7, 21))

    def test_gerar_alertas_ferias_5dias_cria_quando_nao_existe(self):
        ferias = SimpleNamespace(
            id=1,
            data_inicio=date(2026, 7, 10),
            data_fim=date(2026, 7, 20),
            usuario=SimpleNamespace(nome="Gabriel"),
        )

        with (
            patch(
                "app.services.alertas_service.alertas_repository.listar_ferias_aprovadas_por_data_inicio",
                return_value=[ferias],
            ),
            patch(
                "app.services.alertas_service.alertas_repository.existe_alerta_por_ferias_e_tipo",
                return_value=False,
            ),
            patch("app.services.alertas_service.alertas_repository.adicionar_alerta") as adicionar,
            patch("app.services.alertas_service.alertas_repository.salvar_alertas") as salvar,
        ):
            alertas_service.gerar_alertas_ferias_5dias(SimpleNamespace(), hoje=date(2026, 7, 5))

        adicionar.assert_called_once()
        self.assertEqual(adicionar.call_args[0][1].tipo, alertas_service.TIPO_FERIAS_5_DIAS)
        salvar.assert_called_once()

    def test_gerar_alertas_ferias_5dias_nao_duplica(self):
        ferias = SimpleNamespace(
            id=1,
            data_inicio=date(2026, 7, 10),
            data_fim=date(2026, 7, 20),
            usuario=None,
        )

        with (
            patch(
                "app.services.alertas_service.alertas_repository.listar_ferias_aprovadas_por_data_inicio",
                return_value=[ferias],
            ),
            patch(
                "app.services.alertas_service.alertas_repository.existe_alerta_por_ferias_e_tipo",
                return_value=True,
            ),
            patch("app.services.alertas_service.alertas_repository.adicionar_alerta") as adicionar,
            patch("app.services.alertas_service.alertas_repository.salvar_alertas") as salvar,
        ):
            alertas_service.gerar_alertas_ferias_5dias(SimpleNamespace(), hoje=date(2026, 7, 5))

        adicionar.assert_not_called()
        salvar.assert_called_once()

    def test_gerar_alertas_ferias_4dias_cria_quando_nao_existe(self):
        ferias = SimpleNamespace(
            id=1,
            data_inicio=date(2026, 7, 9),
            data_fim=date(2026, 7, 19),
            usuario=SimpleNamespace(nome="Gabriel"),
        )

        with (
            patch(
                "app.services.alertas_service.alertas_repository.listar_ferias_aprovadas_por_intervalo_data_inicio",
                return_value=[ferias],
            ) as listar_intervalo,
            patch(
                "app.services.alertas_service.alertas_repository.existe_alerta_por_ferias_e_tipo",
                return_value=False,
            ),
            patch("app.services.alertas_service.alertas_repository.adicionar_alerta") as adicionar,
            patch("app.services.alertas_service.alertas_repository.salvar_alertas") as salvar,
        ):
            alertas_service.gerar_alertas_ferias_4dias(SimpleNamespace(), hoje=date(2026, 7, 5))

        adicionar.assert_called_once()
        self.assertEqual(adicionar.call_args[0][1].tipo, alertas_service.TIPO_FERIAS_4_DIAS)
        salvar.assert_called_once()
        listar_intervalo.assert_called_once_with(
            ANY,
            date(2026, 7, 6),
            date(2026, 7, 11),
        )

    def test_gerar_alertas_contabilidade_cria_quando_nao_existe(self):
        ferias = SimpleNamespace(
            id=1,
            data_inicio=date(2026, 7, 9),
            data_fim=date(2026, 7, 19),
            usuario=SimpleNamespace(nome="Gabriel"),
        )

        with (
            patch(
                "app.services.alertas_service.alertas_repository.listar_ferias_aprovadas_por_intervalo_data_inicio",
                return_value=[ferias],
            ),
            patch(
                "app.services.alertas_service.alertas_repository.existe_alerta_por_ferias_e_tipo",
                return_value=False,
            ),
            patch("app.services.alertas_service.alertas_repository.adicionar_alerta") as adicionar,
            patch("app.services.alertas_service.alertas_repository.salvar_alertas") as salvar,
        ):
            alertas_service.gerar_alertas_contabilidade(SimpleNamespace(), hoje=date(2026, 7, 5))

        adicionar.assert_called_once()
        salvar.assert_called_once()

    def test_gerar_alertas_contabilidade_nao_duplica(self):
        ferias = SimpleNamespace(
            id=1,
            data_inicio=date(2026, 7, 9),
            data_fim=date(2026, 7, 19),
            usuario=None,
        )

        with (
            patch(
                "app.services.alertas_service.alertas_repository.listar_ferias_aprovadas_por_intervalo_data_inicio",
                return_value=[ferias],
            ),
            patch(
                "app.services.alertas_service.alertas_repository.existe_alerta_por_ferias_e_tipo",
                return_value=True,
            ),
            patch("app.services.alertas_service.alertas_repository.adicionar_alerta") as adicionar,
            patch("app.services.alertas_service.alertas_repository.salvar_alertas") as salvar,
        ):
            alertas_service.gerar_alertas_contabilidade(SimpleNamespace(), hoje=date(2026, 7, 5))

        adicionar.assert_not_called()
        salvar.assert_called_once()

    def test_geradores_nao_confirmam_transacao_quando_commit_desabilitado(self):
        with (
            patch(
                "app.services.alertas_service.alertas_repository.listar_ferias_aprovadas_por_data_inicio",
                return_value=[],
            ),
            patch(
                "app.services.alertas_service.alertas_repository.listar_ferias_aprovadas_por_intervalo_data_inicio",
                return_value=[],
            ),
            patch("app.services.alertas_service.alertas_repository.salvar_alertas") as salvar,
        ):
            db = SimpleNamespace()
            alertas_service.gerar_alertas_contabilidade(db, hoje=date(2026, 7, 5), commit=False)
            alertas_service.gerar_alertas_ferias_5dias(db, hoje=date(2026, 7, 5), commit=False)
            alertas_service.gerar_alertas_ferias_4dias(db, hoje=date(2026, 7, 5), commit=False)

        salvar.assert_not_called()

    def test_sincronizar_alertas_executa_geradores_em_uma_transacao(self):
        db = MagicMock()
        db.bind.dialect.name = "sqlite"
        hoje = date(2026, 7, 5)

        with (
            patch("app.services.alertas_service.gerar_alertas_contabilidade") as contabilidade,
            patch("app.services.alertas_service.gerar_alertas_ferias_5dias") as cinco_dias,
            patch("app.services.alertas_service.gerar_alertas_ferias_4dias") as quatro_dias,
        ):
            alertas_service.sincronizar_alertas(db, hoje=hoje)

        contabilidade.assert_called_once_with(db, hoje, commit=False)
        cinco_dias.assert_called_once_with(db, hoje, commit=False)
        quatro_dias.assert_called_once_with(db, hoje, commit=False)
        db.commit.assert_called_once_with()

    def test_gerar_alerta_usa_data_de_sao_paulo(self):
        with (
            patch("app.services.alertas_service.hoje_sao_paulo", return_value=date(2026, 7, 5)),
            patch(
                "app.services.alertas_service.alertas_repository.listar_ferias_aprovadas_por_data_inicio",
                return_value=[],
            ) as listar,
        ):
            alertas_service.gerar_alertas_ferias_5dias(SimpleNamespace(), commit=False)

        listar.assert_called_once_with(ANY, date(2026, 7, 12))

    def test_marcar_lido_ignora_alerta_inexistente(self):
        with (
            patch("app.services.alertas_service.alertas_repository.obter_alerta_por_id", return_value=None),
            patch("app.services.alertas_service.alertas_repository.marcar_alerta_lido") as marcar,
        ):
            alertas_service.marcar_lido(SimpleNamespace(), 1)

        marcar.assert_not_called()

    def test_listar_alertas_nao_grava_nem_gera_dados(self):
        db = SimpleNamespace()
        with (
            patch(
                "app.services.alertas_service.alertas_repository.listar_alertas",
                return_value=[],
            ),
            patch("app.services.alertas_service.gerar_alertas_contabilidade") as contabilidade,
            patch("app.services.alertas_service.gerar_alertas_ferias_5dias") as cinco_dias,
            patch("app.services.alertas_service.gerar_alertas_ferias_4dias") as quatro_dias,
        ):
            self.assertEqual(alertas_service.listar_alertas(db), [])

        contabilidade.assert_not_called()
        cinco_dias.assert_not_called()
        quatro_dias.assert_not_called()


if __name__ == "__main__":
    unittest.main()
