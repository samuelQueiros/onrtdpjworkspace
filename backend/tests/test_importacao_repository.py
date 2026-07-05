import unittest
from types import SimpleNamespace

from app.repositories import importacao_repository


class FakeQuery:
    def __init__(self, result):
        self.result = result
        self.filtered = False

    def filter(self, *_args):
        self.filtered = True
        return self

    def first(self):
        return self.result


class FakeDb:
    def __init__(self, query_result=None):
        self.query_result = query_result
        self.added = []
        self.committed = False
        self.last_query = None

    def query(self, _model):
        self.last_query = FakeQuery(self.query_result)
        return self.last_query

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True


class ImportacaoRepositoryTests(unittest.TestCase):
    def test_obter_usuario_por_email_filtra(self):
        user = SimpleNamespace(id=1)
        db = FakeDb(query_result=user)

        self.assertEqual(importacao_repository.obter_usuario_por_email(db, "admin@sistema.com"), user)
        self.assertTrue(db.last_query.filtered)

    def test_existe_ferias_periodo_retorna_booleano(self):
        db = FakeDb(query_result=SimpleNamespace(id=1))

        self.assertTrue(importacao_repository.existe_ferias_periodo(db, 1, SimpleNamespace(), SimpleNamespace()))
        self.assertTrue(db.last_query.filtered)

    def test_adicionar_ferias_adiciona_objeto(self):
        ferias = SimpleNamespace(id=1)
        db = FakeDb()

        importacao_repository.adicionar_ferias(db, ferias)

        self.assertEqual(db.added, [ferias])

    def test_commit_persiste(self):
        db = FakeDb()

        importacao_repository.commit(db)

        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
