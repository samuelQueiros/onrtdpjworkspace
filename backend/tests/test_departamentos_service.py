import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.schemas.departamento import DepartamentoCreate, DepartamentoUpdate
from app.services import departamentos_service


class DepartamentosServiceTests(unittest.TestCase):
    def test_validar_nome_disponivel_rejeita_nome_existente(self):
        with patch(
            "app.services.departamentos_service.departamentos_repository.obter_departamento_por_nome",
            return_value=SimpleNamespace(id=1),
        ):
            with self.assertRaises(HTTPException) as exc:
                departamentos_service.validar_nome_disponivel(SimpleNamespace(), "RH")

        self.assertEqual(exc.exception.status_code, 400)

    def test_buscar_departamento_retorna_404_quando_nao_existe(self):
        with patch(
            "app.services.departamentos_service.departamentos_repository.obter_departamento_por_id",
            return_value=None,
        ):
            with self.assertRaises(HTTPException) as exc:
                departamentos_service.buscar_departamento(SimpleNamespace(), 1)

        self.assertEqual(exc.exception.status_code, 404)

    def test_formatar_departamento_inclui_total_quando_solicitado(self):
        departamento = SimpleNamespace(id=1, nome="RH", limite_simultaneo=2, criado_em=None)

        with patch(
            "app.services.departamentos_service.departamentos_repository.contar_usuarios_por_departamento",
            return_value=5,
        ):
            response = departamentos_service.formatar_departamento(
                SimpleNamespace(),
                departamento,
                incluir_total=True,
            )

        self.assertEqual(response["total_usuarios"], 5)

    def test_criar_departamento_salva_com_log(self):
        current_user = SimpleNamespace(id=1)
        payload = DepartamentoCreate(nome="RH", limite_simultaneo=2)

        with (
            patch("app.services.departamentos_service.validar_nome_disponivel"),
            patch("app.services.departamentos_service.departamentos_repository.salvar_departamento_com_log") as salvar,
        ):
            response = departamentos_service.criar_departamento(SimpleNamespace(), payload, current_user)

        self.assertEqual(response["nome"], "RH")
        salvar.assert_called_once()

    def test_editar_departamento_atualiza_campos(self):
        departamento = SimpleNamespace(id=1, nome="RH", limite_simultaneo=2, criado_em=None)
        current_user = SimpleNamespace(id=2)
        payload = DepartamentoUpdate(nome="Financeiro", limite_simultaneo=3)

        with (
            patch("app.services.departamentos_service.buscar_departamento", return_value=departamento),
            patch("app.services.departamentos_service.validar_nome_disponivel"),
            patch("app.services.departamentos_service.departamentos_repository.atualizar_departamento_com_log"),
        ):
            response = departamentos_service.editar_departamento(SimpleNamespace(), 1, payload, current_user)

        self.assertEqual(response["nome"], "Financeiro")
        self.assertEqual(response["limite_simultaneo"], 3)


if __name__ == "__main__":
    unittest.main()
