from datetime import date, datetime
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.schemas.ferias import FeriasCreate, FeriasUpdate
from app.services import ferias_service


class FeriasServiceTests(unittest.TestCase):
    def test_calcular_dias_inclui_inicio_e_fim(self):
        self.assertEqual(ferias_service.calcular_dias(date(2026, 7, 6), date(2026, 7, 10)), 5)

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

        with patch("app.services.ferias_service.buscar_ferias", return_value=ferias):
            with self.assertRaises(HTTPException) as exc:
                ferias_service.editar_ferias(SimpleNamespace(), 1, payload, current_user)

        self.assertEqual(exc.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
