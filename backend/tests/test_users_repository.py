import unittest
from types import SimpleNamespace

from app.repositories import users_repository


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


class UsersRepositoryTests(unittest.TestCase):
    def test_obter_usuario_por_id_filtra_por_id(self):
        user = SimpleNamespace(id=1)
        db = FakeDb(query_result=user)

        self.assertEqual(users_repository.obter_usuario_por_id(db, 1), user)
        self.assertTrue(db.last_query.filtered)

    def test_listar_usuarios_ordena_por_nome(self):
        users = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=users)

        self.assertEqual(users_repository.listar_usuarios(db), users)
        self.assertTrue(db.last_query.ordered)

    def test_salvar_usuario_com_log_atribui_id_ao_log_quando_ausente(self):
        user = SimpleNamespace(id=10)
        log = SimpleNamespace(user_id=None)
        db = FakeDb()

        users_repository.salvar_usuario_com_log(db, user, log)

        self.assertEqual(db.added, [user, log])
        self.assertEqual(log.user_id, 10)
        self.assertTrue(db.flushed)
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, user)

    def test_excluir_usuario_com_log_registra_log_e_exclui(self):
        user = SimpleNamespace(id=1)
        log = SimpleNamespace(user_id=2)
        db = FakeDb()

        users_repository.excluir_usuario_com_log(db, user, log)

        self.assertEqual(db.added, [log])
        self.assertEqual(db.deleted, [user])
        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
