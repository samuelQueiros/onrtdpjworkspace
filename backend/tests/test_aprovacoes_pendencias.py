import unittest
from unittest.mock import patch

from app.routers.autorizacoes_equipamentos import contar_pendencias


class FakeQuery:
    def filter(self, *_args):
        return self

    def count(self):
        return 4


class FakeDb:
    def query(self, *_args):
        return FakeQuery()


class AprovacoesPendenciasTests(unittest.TestCase):
    def test_agrega_pendencias_de_ferias_e_equipamentos(self):
        with patch(
            "app.routers.autorizacoes_equipamentos.autorizacoes_equipamentos_service.contar_pendentes",
            return_value=3,
        ):
            resultado = contar_pendencias(db=FakeDb(), _=None)

        self.assertEqual(resultado, {"ferias": 4, "equipamentos": 3, "total": 7})


if __name__ == "__main__":
    unittest.main()
