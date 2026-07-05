import unittest
from types import SimpleNamespace

from app.repositories import departamentos_repository


class FakeQuery:
    def __init__(self, result=0):
        self.result = result
        self.filtered = False
        self.ordered = False
        self.updated = None

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

    def count(self):
        return self.result

    def update(self, value):
        self.updated = value


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


class DepartamentosRepositoryTests(unittest.TestCase):
    def test_listar_departamentos_ordena_por_nome(self):
        departamentos = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=departamentos)

        self.assertEqual(departamentos_repository.listar_departamentos(db), departamentos)
        self.assertTrue(db.last_query.ordered)

    def test_contar_usuarios_por_departamento_filtra_e_conta(self):
        db = FakeDb(query_result=3)

        self.assertEqual(departamentos_repository.contar_usuarios_por_departamento(db, 1), 3)
        self.assertTrue(db.last_query.filtered)

    def test_salvar_departamento_com_log_persiste(self):
        departamento = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        departamentos_repository.salvar_departamento_com_log(db, departamento, log)

        self.assertEqual(db.added, [departamento, log])
        self.assertTrue(db.flushed)
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, departamento)

    def test_excluir_departamento_com_log_desvincula_usuarios(self):
        departamento = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        departamentos_repository.excluir_departamento_com_log(db, departamento, log)

        self.assertEqual(db.last_query.updated, {"departamento_id": None})
        self.assertEqual(db.added, [log])
        self.assertEqual(db.deleted, [departamento])
        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
