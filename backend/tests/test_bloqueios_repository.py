import unittest
from types import SimpleNamespace

from app.repositories import bloqueios_repository


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


class BloqueiosRepositoryTests(unittest.TestCase):
    def test_listar_bloqueios_ordena_por_data_inicio(self):
        bloqueios = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=bloqueios)

        self.assertEqual(bloqueios_repository.listar_bloqueios(db), bloqueios)
        self.assertTrue(db.last_query.ordered)

    def test_obter_bloqueio_por_id_filtra(self):
        bloqueio = SimpleNamespace(id=1)
        db = FakeDb(query_result=bloqueio)

        self.assertEqual(bloqueios_repository.obter_bloqueio_por_id(db, 1), bloqueio)
        self.assertTrue(db.last_query.filtered)

    def test_salvar_bloqueio_com_log_persiste(self):
        bloqueio = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        bloqueios_repository.salvar_bloqueio_com_log(db, bloqueio, log)

        self.assertEqual(db.added, [bloqueio, log])
        self.assertTrue(db.flushed)
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, bloqueio)

    def test_excluir_bloqueio_com_log_registra_e_exclui(self):
        bloqueio = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        bloqueios_repository.excluir_bloqueio_com_log(db, bloqueio, log)

        self.assertEqual(db.added, [log])
        self.assertEqual(db.deleted, [bloqueio])
        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
