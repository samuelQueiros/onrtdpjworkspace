import unittest
from types import SimpleNamespace

from app.repositories import bootstrap_repository


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
        self.flushed = False
        self.refreshed = None
        self.last_query = None

    def query(self, _model):
        self.last_query = FakeQuery(self.query_result)
        return self.last_query

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def flush(self):
        self.flushed = True

    def refresh(self, obj):
        self.refreshed = obj


class BootstrapRepositoryTests(unittest.TestCase):
    def test_obter_admin_filtra_por_role(self):
        admin = SimpleNamespace(id=1)
        db = FakeDb(query_result=admin)

        self.assertEqual(bootstrap_repository.obter_admin(db), admin)
        self.assertTrue(db.last_query.filtered)

    def test_salvar_admin_com_log_persiste_e_preenche_user_id(self):
        admin = SimpleNamespace(id=1)
        log = SimpleNamespace(user_id=None)
        db = FakeDb()

        bootstrap_repository.salvar_admin_com_log(db, admin, log)

        self.assertEqual(db.added, [admin, log])
        self.assertEqual(log.user_id, 1)
        self.assertTrue(db.flushed)
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, admin)


if __name__ == "__main__":
    unittest.main()
