from datetime import date, datetime, timedelta
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.schemas.ferias import FeriasCreate, FeriasUpdate
from app.services import ferias_service


def _proxima_segunda() -> date:
    hoje = date.today()
    dias_ate_segunda = (7 - hoje.weekday()) % 7 or 7
    return hoje + timedelta(days=dias_ate_segunda)


class FeriasServiceTests(unittest.TestCase):
    def test_calcular_dias_inclui_inicio_e_fim(self):
        self.assertEqual(ferias_service.calcular_dias(date(2026, 7, 6), date(2026, 7, 10)), 5)

    def test_verificar_regras_data_bloqueia_quinta_e_sexta(self):
        segunda = _proxima_segunda()
        with patch("app.services.ferias_service.feriados_br", return_value=set()):
            for delta in (3, 4):  # quinta, sexta
                with self.assertRaises(HTTPException) as exc:
                    ferias_service.verificar_regras_data(segunda + timedelta(days=delta), segunda + timedelta(days=delta))
                self.assertEqual(exc.exception.status_code, 400)

    def test_verificar_regras_data_bloqueia_fim_de_semana(self):
        segunda = _proxima_segunda()
        with patch("app.services.ferias_service.feriados_br", return_value=set()):
            for delta in (5, 6):  # sabado, domingo
                with self.assertRaises(HTTPException) as exc:
                    ferias_service.verificar_regras_data(segunda + timedelta(days=delta), segunda + timedelta(days=delta))
                self.assertIn("DSR", exc.exception.detail)

    def test_verificar_regras_data_permite_segunda_terca_quarta_sem_feriado(self):
        segunda = _proxima_segunda()
        with patch("app.services.ferias_service.feriados_br", return_value=set()):
            for delta in (0, 1, 2):
                ferias_service.verificar_regras_data(segunda + timedelta(days=delta), segunda + timedelta(days=delta))

    def test_verificar_regras_data_bloqueia_dois_dias_antes_do_feriado(self):
        segunda = _proxima_segunda()
        feriado = segunda + timedelta(days=3)  # quinta-feira
        with patch("app.services.ferias_service.feriados_br", return_value={feriado}):
            # terca e quarta ficam a 2 e 1 dia(s) do feriado de quinta: devem ser bloqueadas
            for delta in (1, 2):
                with self.assertRaises(HTTPException) as exc:
                    ferias_service.verificar_regras_data(segunda + timedelta(days=delta), segunda + timedelta(days=delta))
                self.assertIn("feriado", exc.exception.detail)
            # segunda esta a 3 dias do feriado: permitida
            ferias_service.verificar_regras_data(segunda, segunda)

    def test_verificar_regras_data_bloqueio_funciona_atravessando_fronteira_de_semana(self):
        segunda = _proxima_segunda()
        proxima_semana_quarta = segunda + timedelta(days=9)  # quarta-feira da semana seguinte
        with patch("app.services.ferias_service.feriados_br", return_value={proxima_semana_quarta}):
            # segunda e terca da semana seguinte ficam a 2 e 1 dia(s) do feriado, mesmo em semanas diferentes do calculo
            segunda_seguinte = segunda + timedelta(days=7)
            for delta in (0, 1):
                with self.assertRaises(HTTPException) as exc:
                    ferias_service.verificar_regras_data(segunda_seguinte + timedelta(days=delta), segunda_seguinte + timedelta(days=delta))
                self.assertIn("feriado", exc.exception.detail)

    def test_verificar_regras_data_bloqueia_inicio_no_proprio_feriado(self):
        segunda = _proxima_segunda()
        with patch("app.services.ferias_service.feriados_br", return_value={segunda}):
            with self.assertRaises(HTTPException) as exc:
                ferias_service.verificar_regras_data(segunda, segunda)
            self.assertIn("feriado", exc.exception.detail)

    def test_verificar_regras_data_bloqueia_feriado_na_terca_ou_quarta(self):
        segunda = _proxima_segunda()
        feriado = segunda + timedelta(days=2)  # quarta-feira
        with patch("app.services.ferias_service.feriados_br", return_value={feriado}):
            # a propria quarta (feriado), e a segunda e terca (2 e 1 dia antes) ficam bloqueadas
            for delta in (0, 1, 2):
                with self.assertRaises(HTTPException) as exc:
                    ferias_service.verificar_regras_data(segunda + timedelta(days=delta), segunda + timedelta(days=delta))
                self.assertIn("feriado", exc.exception.detail)

    def test_calcular_anos_completos_conta_anos_fechados(self):
        hoje = date(2026, 7, 23)
        self.assertEqual(ferias_service.calcular_anos_completos(date(2020, 1, 10), hoje=hoje), 6)
        self.assertEqual(ferias_service.calcular_anos_completos(date(2020, 8, 10), hoje=hoje), 5)
        self.assertEqual(ferias_service.calcular_anos_completos(None, hoje=hoje), 0)
        self.assertEqual(ferias_service.calcular_anos_completos(date(2027, 1, 1), hoje=hoje), 0)

    def test_calcular_extrato_usa_movimentos_e_nao_tempo_de_admissao(self):
        user = SimpleNamespace(id=1, dias_totais=30, data_admissao=date(2020, 1, 1))
        marco = datetime(2026, 7, 1)
        movimentos = [
            SimpleNamespace(quantidade_dias=15, criado_em=marco),
            SimpleNamespace(quantidade_dias=5, criado_em=datetime(2026, 7, 2)),
        ]
        ferias_fake = [SimpleNamespace(dias_usados=7)]

        with (
            patch("app.services.ferias_service.sincronizar_creditos_anuais"),
            patch("app.services.ferias_service.ferias_repository.listar_movimentos_saldo", return_value=movimentos),
            patch("app.services.ferias_service.ferias_repository.listar_ferias_para_saldo_desde", return_value=ferias_fake),
        ):
            extrato = ferias_service.calcular_extrato_saldo(SimpleNamespace(), user)

        self.assertEqual(extrato["dias_direito_total"], 20)
        self.assertEqual(extrato["dias_usados_total"], 7)
        self.assertEqual(extrato["saldo"], 13)
        self.assertEqual(extrato["vencidas"], [])

    def test_proxima_concessao_usa_aniversario_de_admissao_futuro(self):
        self.assertEqual(
            ferias_service.proxima_concessao_apos(date(2024, 1, 1), date(2026, 7, 26)),
            date(2027, 1, 1),
        )

    def test_credito_anual_e_idempotente_e_avanca_proxima_concessao(self):
        user = SimpleNamespace(
            id=9,
            dias_totais=30,
            data_admissao=date(2024, 1, 1),
            proxima_concessao_ferias=date(2026, 1, 1),
        )
        db = MagicMock()

        with patch(
            "app.services.ferias_service.ferias_repository.obter_movimento_por_chave",
            return_value=None,
        ):
            criados = ferias_service.sincronizar_creditos_anuais(
                db, user, hoje=date(2026, 7, 26)
            )

        self.assertEqual(criados, 1)
        movimento = next(
            chamada.args[0]
            for chamada in db.add.call_args_list
            if chamada.args[0].__class__.__name__ == "SaldoFeriasMovimento"
        )
        self.assertEqual(movimento.quantidade_dias, 30)
        self.assertEqual(movimento.data_referencia, date(2026, 1, 1))
        self.assertEqual(user.proxima_concessao_ferias, date(2027, 1, 1))
        db.commit.assert_called_once()

    def test_calcular_saldo_e_atalho_para_o_saldo_do_extrato(self):
        user = SimpleNamespace(id=1, dias_totais=30, data_admissao=date(2020, 1, 1))
        with patch(
            "app.services.ferias_service.calcular_extrato_saldo",
            return_value={"saldo": 42},
        ) as extrato_mock:
            saldo = ferias_service.calcular_saldo(SimpleNamespace(), user, excluir_ferias_id=7)

        extrato_mock.assert_called_once_with(unittest.mock.ANY, user, 7)
        self.assertEqual(saldo, 42)

    def test_buscar_ferias_retorna_404_quando_nao_existe(self):
        with patch("app.services.ferias_service.ferias_repository.obter_ferias_por_id", return_value=None):
            with self.assertRaises(HTTPException) as exc:
                ferias_service.buscar_ferias(SimpleNamespace(), 1)

        self.assertEqual(exc.exception.status_code, 404)

    def test_formatar_ferias_inclui_usuario_e_aprovador(self):
        ferias = SimpleNamespace(
            id=1,
            user_id=2,
            usuario=SimpleNamespace(nome="Gabriel", cor="#ffffff"),
            data_inicio=date(2026, 7, 6),
            data_fim=date(2026, 7, 10),
            dias_usados=5,
            status="aprovada",
            ferias_acordo=False,
            motivo_rejeicao=None,
            criado_em=datetime(2026, 7, 1),
            aprovado_por_id=3,
            aprovado_por=SimpleNamespace(nome="Admin"),
            aprovado_em=datetime(2026, 7, 2),
            rejeitado_por_id=None,
            rejeitado_por=None,
            rejeitado_em=None,
        )

        response = ferias_service.formatar_ferias(ferias)

        self.assertEqual(response["nome_usuario"], "Gabriel")
        self.assertEqual(response["aprovado_por_nome"], "Admin")

    def test_registrar_ferias_de_usuario_comum_cria_pendente(self):
        payload = FeriasCreate(data_inicio=date(2027, 7, 5), data_fim=date(2027, 7, 9))
        current_user = SimpleNamespace(
            id=1,
            role="user",
            departamento_id=None,
            data_admissao=None,
            dias_totais=30,
        )

        with (
            patch("app.services.ferias_service.verificar_regras_data"),
            patch("app.services.ferias_service.verificar_bloqueio_datas"),
            patch("app.services.ferias_service.verificar_sobreposicao_departamento", return_value=False),
            patch("app.services.ferias_service.calcular_saldo", return_value=30),
            patch("app.services.ferias_service.ferias_repository.salvar_ferias_com_log") as salvar,
        ):
            response = ferias_service.registrar_ferias(SimpleNamespace(), payload, current_user)

        salvar.assert_called_once()
        self.assertEqual(response["status"], "pendente")
        self.assertEqual(response["dias_usados"], 5)

    def test_editar_ferias_bloqueia_usuario_em_ferias_aprovadas(self):
        ferias = SimpleNamespace(
            id=1,
            user_id=1,
            status="aprovada",
            data_inicio=date(2027, 7, 5),
            data_fim=date(2027, 7, 9),
            ferias_acordo=False,
        )
        current_user = SimpleNamespace(id=1, role="user")
        payload = FeriasUpdate(data_inicio=date(2027, 7, 12))

        with patch("app.services.ferias_service.buscar_ferias_para_atualizar", return_value=ferias):
            with self.assertRaises(HTTPException) as exc:
                ferias_service.editar_ferias(SimpleNamespace(), 1, payload, current_user)

        self.assertEqual(exc.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
