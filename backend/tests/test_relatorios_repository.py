import unittest
from types import SimpleNamespace

from app.repositories import relatorios_repository


class FakeQuery:
    def __init__(self, result):
        self.result = result
        self.filtered = False
        self.ordered = False

    def filter(self, *_args):
        self.filtered = True
        return self

    def order_by(self, *_args):
        self.ordered = True
        return self

    def all(self):
        return self.result

    def count(self):
        return self.result


class FakeDb:
    def __init__(self, query_result=None):
        self.query_result = query_result
        self.last_query = None

    def query(self, _model):
        self.last_query = FakeQuery(self.query_result)
        return self.last_query


class RelatoriosRepositoryTests(unittest.TestCase):
    def test_listar_usuarios_ordenados_ordena_por_nome(self):
        users = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=users)

        self.assertEqual(relatorios_repository.listar_usuarios_ordenados(db), users)
        self.assertTrue(db.last_query.ordered)

    def test_listar_ferias_aprovadas_ciclo_filtra(self):
        ferias = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=ferias)

        self.assertEqual(relatorios_repository.listar_ferias_aprovadas_ciclo(db, 1, SimpleNamespace()), ferias)
        self.assertTrue(db.last_query.filtered)

    def test_contar_colaboradores_filtra(self):
        db = FakeDb(query_result=3)

        self.assertEqual(relatorios_repository.contar_colaboradores(db), 3)
        self.assertTrue(db.last_query.filtered)

    def test_listar_logs_ordena(self):
        logs = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=logs)

        self.assertEqual(relatorios_repository.listar_logs(db), logs)
        self.assertTrue(db.last_query.ordered)


if __name__ == "__main__":
    unittest.main()
