import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from app.models.patrimonio import SolicitacaoEquipamento
from app.repositories import patrimonios_repository


class FakeQuery:
    def __init__(self):
        self.distinct_aplicado = False
        self.ordenacao = ()

    def join(self, *_args):
        return self

    def filter(self, *_args):
        return self

    def distinct(self):
        self.distinct_aplicado = True
        return self

    def order_by(self, *args):
        self.ordenacao = args
        return self

    def all(self):
        return [(7, datetime(2026, 7, 13, tzinfo=timezone.utc))]


class FakeDb:
    def __init__(self):
        self.colunas = ()
        self.query_obj = FakeQuery()

    def query(self, *colunas):
        self.colunas = colunas
        return self.query_obj


class PatrimoniosRepositoryTests(unittest.TestCase):
    def test_listagem_admin_inclui_coluna_de_ordenacao_no_select_distinct(self):
        db = FakeDb()

        with patch.object(
            patrimonios_repository,
            "obter_solicitacao",
            side_effect=lambda _db, item_id: SimpleNamespace(id=item_id),
        ):
            resultado = patrimonios_repository.listar_solicitacoes_admin(db, status="pendente")

        self.assertEqual(db.colunas, (SolicitacaoEquipamento.id, SolicitacaoEquipamento.criado_em))
        self.assertTrue(db.query_obj.distinct_aplicado)
        self.assertEqual(len(db.query_obj.ordenacao), 2)
        self.assertEqual([item.id for item in resultado], [7])


if __name__ == "__main__":
    unittest.main()
