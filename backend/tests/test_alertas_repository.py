import unittest
from types import SimpleNamespace

from app.repositories import alertas_repository


class FakeQuery:
    def __init__(self, result):
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

    def update(self, values):
        self.updated = values
        return 3


class FakeDb:
    def __init__(self, query_result=None):
        self.query_result = query_result
        self.added = []
        self.committed = False
        self.refreshed = None
        self.last_query = None

    def query(self, _model):
        self.last_query = FakeQuery(self.query_result)
        return self.last_query

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed = obj


class AlertasRepositoryTests(unittest.TestCase):
    def test_listar_ferias_aprovadas_por_data_inicio_filtra(self):
        ferias = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=ferias)

        self.assertEqual(alertas_repository.listar_ferias_aprovadas_por_data_inicio(db, SimpleNamespace()), ferias)
        self.assertTrue(db.last_query.filtered)

    def test_listar_ferias_aprovadas_por_intervalo_filtra_e_ordena(self):
        ferias = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=ferias)

        resultado = alertas_repository.listar_ferias_aprovadas_por_intervalo_data_inicio(
            db,
            SimpleNamespace(),
            SimpleNamespace(),
        )

        self.assertEqual(resultado, ferias)
        self.assertTrue(db.last_query.filtered)
        self.assertTrue(db.last_query.ordered)

    def test_existe_alerta_por_ferias_e_tipo_retorna_booleano(self):
        db = FakeDb(query_result=SimpleNamespace(id=1))

        self.assertTrue(alertas_repository.existe_alerta_por_ferias_e_tipo(db, 1, "tipo"))
        self.assertTrue(db.last_query.filtered)

    def test_listar_alertas_ordena(self):
        alertas = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=alertas)

        self.assertEqual(alertas_repository.listar_alertas(db), alertas)
        self.assertTrue(db.last_query.ordered)

    def test_marcar_alerta_lido_persiste(self):
        alerta = SimpleNamespace(id=1, lido=False)
        db = FakeDb()

        alertas_repository.marcar_alerta_lido(db, alerta)

        self.assertTrue(alerta.lido)
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, alerta)

    def test_marcar_todos_lidos_atualiza_em_lote(self):
        db = FakeDb()

        total = alertas_repository.marcar_todos_lidos(db)

        self.assertEqual(total, 3)
        self.assertEqual(db.last_query.updated, {"lido": True})
        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
