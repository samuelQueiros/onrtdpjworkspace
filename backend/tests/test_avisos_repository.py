import unittest
from types import SimpleNamespace

from app.repositories import avisos_repository


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


class AvisosRepositoryTests(unittest.TestCase):
    def test_listar_avisos_ativos_filtra_e_ordena(self):
        avisos = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=avisos)

        self.assertEqual(avisos_repository.listar_avisos_ativos(db, SimpleNamespace()), avisos)
        self.assertTrue(db.last_query.filtered)
        self.assertTrue(db.last_query.ordered)

    def test_obter_aviso_por_id_filtra(self):
        aviso = SimpleNamespace(id=1)
        db = FakeDb(query_result=aviso)

        self.assertEqual(avisos_repository.obter_aviso_por_id(db, 1), aviso)
        self.assertTrue(db.last_query.filtered)

    def test_salvar_aviso_com_log_persiste(self):
        aviso = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        avisos_repository.salvar_aviso_com_log(db, aviso, log)

        self.assertEqual(db.added, [aviso, log])
        self.assertTrue(db.flushed)
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, aviso)

    def test_excluir_aviso_com_log_registra_e_exclui(self):
        aviso = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        avisos_repository.excluir_aviso_com_log(db, aviso, log)

        self.assertEqual(db.added, [log])
        self.assertEqual(db.deleted, [aviso])
        self.assertTrue(db.committed)

    def test_salvar_aviso_com_log_none_nao_adiciona_log(self):
        aviso = SimpleNamespace(id=1)
        db = FakeDb()

        avisos_repository.salvar_aviso_com_log(db, aviso, None)

        self.assertEqual(db.added, [aviso])
        self.assertTrue(db.committed)

    def test_excluir_aviso_com_log_none_nao_adiciona_log(self):
        aviso = SimpleNamespace(id=1)
        db = FakeDb()

        avisos_repository.excluir_aviso_com_log(db, aviso, None)

        self.assertEqual(db.added, [])
        self.assertEqual(db.deleted, [aviso])
        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
