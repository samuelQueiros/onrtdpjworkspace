import unittest
from types import SimpleNamespace

from app.repositories import credenciais_repository


class FakeQuery:
    def __init__(self, result):
        self.result = result
        self.filtered = False
        self.ordered = False
        self.joined = False
        self.deleted = False

    def filter(self, *_args):
        self.filtered = True
        return self

    def order_by(self, *_args):
        self.ordered = True
        return self

    def join(self, *_args):
        self.joined = True
        return self

    def first(self):
        return self.result

    def all(self):
        return self.result

    def delete(self):
        self.deleted = True


class FakeDb:
    def __init__(self, query_result=None):
        self.query_result = query_result
        self.added = []
        self.deleted = []
        self.committed = False
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

    def refresh(self, obj):
        self.refreshed = obj


class CredenciaisRepositoryTests(unittest.TestCase):
    def test_obter_credencial_por_id_filtra_por_id(self):
        credencial = SimpleNamespace(id=1)
        db = FakeDb(query_result=credencial)

        self.assertEqual(credenciais_repository.obter_credencial_por_id(db, 1), credencial)
        self.assertTrue(db.last_query.filtered)

    def test_listar_credenciais_ordena_por_descricao(self):
        credenciais = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=credenciais)

        self.assertEqual(credenciais_repository.listar_credenciais(db), credenciais)
        self.assertTrue(db.last_query.ordered)

    def test_listar_credenciais_por_usuario_faz_join_e_filtro(self):
        credenciais = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=credenciais)

        self.assertEqual(credenciais_repository.listar_credenciais_por_usuario(db, 2), credenciais)
        self.assertTrue(db.last_query.joined)
        self.assertTrue(db.last_query.filtered)

    def test_salvar_credencial_persiste_e_atualiza(self):
        credencial = SimpleNamespace(id=None)
        db = FakeDb()

        result = credenciais_repository.salvar_credencial(db, credencial)

        self.assertEqual(result, credencial)
        self.assertEqual(db.added, [credencial])
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, credencial)

    def test_substituir_permissoes_remove_e_recria_acessos(self):
        db = FakeDb()

        credenciais_repository.substituir_permissoes(db, 1, [2, 3])

        self.assertTrue(db.last_query.filtered)
        self.assertTrue(db.last_query.deleted)
        self.assertEqual(len(db.added), 2)
        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
