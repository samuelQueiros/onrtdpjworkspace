import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.schemas.cargo import CargoCreate, CargoUpdate
from app.services import cargos_service


class CargosServiceTests(unittest.TestCase):
    def test_criar_cargo_rejeita_nome_duplicado(self):
        with patch(
            "app.services.cargos_service.cargos_repository.obter_cargo_por_nome",
            return_value=SimpleNamespace(id=1),
        ):
            with self.assertRaises(HTTPException) as exc:
                cargos_service.criar_cargo(
                    SimpleNamespace(),
                    CargoCreate(nome="Desenvolvedor"),
                    SimpleNamespace(id=1),
                )

        self.assertEqual(exc.exception.status_code, 400)

    def test_validar_cargo_rejeita_cargo_nao_cadastrado(self):
        with patch(
            "app.services.cargos_service.cargos_repository.obter_cargo_por_nome",
            return_value=None,
        ):
            with self.assertRaises(HTTPException) as exc:
                cargos_service.validar_cargo(SimpleNamespace(), "Cargo inexistente")

        self.assertEqual(exc.exception.status_code, 400)

    def test_editar_cargo_preserva_vinculos_pelo_nome(self):
        cargo = SimpleNamespace(id=3, nome="Analista", criado_em=None)
        with (
            patch("app.services.cargos_service.cargos_repository.obter_cargo_por_id", return_value=cargo),
            patch("app.services.cargos_service.cargos_repository.obter_cargo_por_nome_exceto_id", return_value=None),
            patch("app.services.cargos_service.cargos_repository.atualizar_com_log") as renomear,
            patch("app.services.cargos_service.cargos_repository.contar_usuarios", return_value=2),
        ):
            response = cargos_service.editar_cargo(
                SimpleNamespace(),
                3,
                CargoUpdate(nome="Analista de BI"),
                SimpleNamespace(id=1),
            )

        renomear.assert_called_once()
        self.assertEqual(response["nome"], "Analista de BI")
        self.assertEqual(response["total_usuarios"], 2)


if __name__ == "__main__":
    unittest.main()
