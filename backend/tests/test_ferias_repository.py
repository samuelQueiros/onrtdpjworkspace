import unittest
from types import SimpleNamespace

from app.repositories import ferias_repository


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

    def first(self):
        return self.result

    def all(self):
        return self.result


class FakeDb:
    def __init__(self, query_result=None):
        self.query_result = query_result
        self.added = []
        self.deleted = []
        self.committed = False
        self.flushed = False
        self.refreshed = None
        self.last_query = None

    def query(self, _model):
        self.last_query = FakeQuery(self.query_result)
        return self.last_query

    def add(self, obj):
        self.added.append(obj)

    def delete(self, obj):
        self.deleted.append(obj)

    def commit(self):
        self.committed = True

    def flush(self):
        self.flushed = True

    def refresh(self, obj):
        self.refreshed = obj


class FeriasRepositoryTests(unittest.TestCase):
    def test_listar_ferias_por_usuario_filtra_e_ordena(self):
        ferias = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=ferias)

        self.assertEqual(ferias_repository.listar_ferias_por_usuario(db, 1), ferias)
        self.assertTrue(db.last_query.filtered)
        self.assertTrue(db.last_query.ordered)

    def test_obter_ferias_por_id_filtra(self):
        ferias = SimpleNamespace(id=1)
        db = FakeDb(query_result=ferias)

        self.assertEqual(ferias_repository.obter_ferias_por_id(db, 1), ferias)
        self.assertTrue(db.last_query.filtered)

    def test_salvar_ferias_com_log_persiste(self):
        ferias = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        ferias_repository.salvar_ferias_com_log(db, ferias, log)

        self.assertEqual(db.added, [ferias, log])
        self.assertTrue(db.flushed)
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, ferias)

    def test_excluir_ferias_com_log_exclui_e_registra(self):
        ferias = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        ferias_repository.excluir_ferias_com_log(db, ferias, log)

        self.assertEqual(db.deleted, [ferias])
        self.assertEqual(db.added, [log])
        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
