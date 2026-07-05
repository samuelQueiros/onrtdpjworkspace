import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.schemas.aviso import AvisoCreate, AvisoUpdate
from app.services import avisos_service


class AvisosServiceTests(unittest.TestCase):
    def test_buscar_aviso_retorna_404_quando_nao_existe(self):
        with patch("app.services.avisos_service.avisos_repository.obter_aviso_por_id", return_value=None):
            with self.assertRaises(HTTPException) as exc:
                avisos_service.buscar_aviso(SimpleNamespace(), 1)

        self.assertEqual(exc.exception.status_code, 404)

    def test_formatar_aviso_usa_sistema_quando_sem_criador(self):
        aviso = SimpleNamespace(
            id=1,
            titulo="Aviso",
            conteudo="Conteudo",
            fixado=False,
            data_expiracao=None,
            criado_por=None,
            criado_em=None,
        )

        response = avisos_service.formatar_aviso(aviso)

        self.assertEqual(response["criado_por_nome"], "Sistema")

    def test_criar_aviso_salva_com_log(self):
        payload = AvisoCreate(titulo="Aviso", conteudo="Conteudo")
        current_user = SimpleNamespace(id=1)

        with patch("app.services.avisos_service.avisos_repository.salvar_aviso_com_log") as salvar:
            response = avisos_service.criar_aviso(SimpleNamespace(), payload, current_user)

        self.assertEqual(response["titulo"], "Aviso")
        salvar.assert_called_once()

    def test_editar_aviso_atualiza_campos(self):
        aviso = SimpleNamespace(
            id=1,
            titulo="Antigo",
            conteudo="Texto",
            fixado=False,
            data_expiracao=None,
            criado_por=None,
            criado_em=None,
        )
        payload = AvisoUpdate(titulo="Novo", fixado=True)

        with (
            patch("app.services.avisos_service.buscar_aviso", return_value=aviso),
            patch("app.services.avisos_service.avisos_repository.atualizar_aviso_com_log"),
        ):
            response = avisos_service.editar_aviso(SimpleNamespace(), 1, payload, SimpleNamespace(id=2))

        self.assertEqual(response["titulo"], "Novo")
        self.assertTrue(response["fixado"])


if __name__ == "__main__":
    unittest.main()
