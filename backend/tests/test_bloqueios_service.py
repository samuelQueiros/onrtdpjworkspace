from datetime import date, datetime
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.schemas.bloqueio import BloqueioCreate, BloqueioUpdate
from app.services import bloqueios_service


class BloqueiosServiceTests(unittest.TestCase):
    def test_buscar_bloqueio_retorna_404_quando_nao_existe(self):
        with patch("app.services.bloqueios_service.bloqueios_repository.obter_bloqueio_por_id", return_value=None):
            with self.assertRaises(HTTPException) as exc:
                bloqueios_service.buscar_bloqueio(SimpleNamespace(), 1)

        self.assertEqual(exc.exception.status_code, 404)

    def test_criar_bloqueio_rejeita_periodo_invalido(self):
        payload = BloqueioCreate(
            data_inicio=date(2026, 7, 10),
            data_fim=date(2026, 7, 9),
            motivo="Fechamento",
        )

        with self.assertRaises(HTTPException) as exc:
            bloqueios_service.criar_bloqueio(SimpleNamespace(), payload, SimpleNamespace(id=1))

        self.assertEqual(exc.exception.status_code, 400)

    def test_criar_bloqueio_rejeita_tipo_invalido(self):
        payload = BloqueioCreate(
            data_inicio=date(2026, 7, 10),
            data_fim=date(2026, 7, 10),
            motivo="Fechamento",
            tipo="feriado",
        )

        with self.assertRaises(HTTPException) as exc:
            bloqueios_service.criar_bloqueio(SimpleNamespace(), payload, SimpleNamespace(id=1))

        self.assertEqual(exc.exception.status_code, 400)

    def test_criar_bloqueio_salva_com_log(self):
        payload = BloqueioCreate(
            data_inicio=date(2026, 7, 10),
            data_fim=date(2026, 7, 12),
            motivo="Recesso",
            tipo="recesso",
        )

        with patch("app.services.bloqueios_service.bloqueios_repository.salvar_bloqueio_com_log") as salvar:
            response = bloqueios_service.criar_bloqueio(SimpleNamespace(), payload, SimpleNamespace(id=1))

        self.assertEqual(response["tipo"], "recesso")
        self.assertEqual(response["motivo"], "Recesso")
        salvar.assert_called_once()

    def test_editar_bloqueio_atualiza_campos(self):
        bloqueio = SimpleNamespace(
            id=1,
            data_inicio=date(2026, 7, 10),
            data_fim=date(2026, 7, 12),
            motivo="Antigo",
            tipo="bloqueio",
            criado_por=None,
            criado_em=datetime(2026, 7, 1),
        )
        payload = BloqueioUpdate(motivo="Novo", tipo="recesso")

        with (
            patch("app.services.bloqueios_service.buscar_bloqueio", return_value=bloqueio),
            patch("app.services.bloqueios_service.bloqueios_repository.atualizar_bloqueio_com_log"),
        ):
            response = bloqueios_service.editar_bloqueio(SimpleNamespace(), 1, payload, SimpleNamespace(id=2))

        self.assertEqual(response["motivo"], "Novo")
        self.assertEqual(response["tipo"], "recesso")


if __name__ == "__main__":
    unittest.main()
