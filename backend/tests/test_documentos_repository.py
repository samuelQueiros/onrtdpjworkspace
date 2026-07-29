import unittest
from types import SimpleNamespace

from app.repositories import documentos_repository


class FakeQuery:
    def __init__(self, result):
        self.result = result
        self.filtered = False
        self.ordered = False
        self.offset_value = None
        self.limit_value = None

    def filter(self, *_args):
        self.filtered = True
        return self

    def join(self, *_args):
        return self

    def options(self, *_args):
        return self

    def order_by(self, *_args):
        self.ordered = True
        return self

    def first(self):
        return self.result

    def offset(self, value):
        self.offset_value = value
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def count(self):
        return len(self.result)

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


class DocumentosRepositoryTests(unittest.TestCase):
    def test_obter_documento_por_id_retorna_primeiro_resultado(self):
        doc = SimpleNamespace(id=1)
        db = FakeDb(query_result=doc)

        self.assertEqual(documentos_repository.obter_documento_por_id(db, 1), doc)
        self.assertTrue(db.last_query.filtered)

    def test_listar_documentos_por_usuario_ordena_por_criacao(self):
        docs = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
        db = FakeDb(query_result=docs)

        self.assertEqual(documentos_repository.listar_documentos_por_usuario(db, 1), docs)
        self.assertTrue(db.last_query.filtered)
        self.assertTrue(db.last_query.ordered)

    def test_listar_historico_paginado_filtra_ordena_e_limita(self):
        docs = [SimpleNamespace(id=1)]
        db = FakeDb(query_result=docs)

        resultado = documentos_repository.listar_historico_paginado(
            db,
            "enviados",
            usuario_id=1,
            filtro_usuario_id=2,
            offset=10,
            limit=10,
        )

        self.assertEqual(resultado, docs)
        self.assertTrue(db.last_query.filtered)
        self.assertTrue(db.last_query.ordered)
        self.assertEqual(db.last_query.offset_value, 10)
        self.assertEqual(db.last_query.limit_value, 10)

    def test_contar_historico_retorna_total_filtrado(self):
        db = FakeDb(query_result=[SimpleNamespace(id=1), SimpleNamespace(id=2)])

        total = documentos_repository.contar_historico(
            db,
            "recebidos_administracao",
            usuario_id=1,
            filtro_usuario_id=None,
        )

        self.assertEqual(total, 2)
        self.assertTrue(db.last_query.filtered)

    def test_salvar_documento_com_log_persiste_e_atualiza_documento(self):
        doc = SimpleNamespace(id=None)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        result = documentos_repository.salvar_documento_com_log(db, doc, log)

        self.assertEqual(result, doc)
        self.assertEqual(db.added, [doc, log])
        self.assertTrue(db.flushed)
        self.assertTrue(db.committed)
        self.assertEqual(db.refreshed, doc)

    def test_excluir_documento_com_log_registra_log_e_exclui_documento(self):
        doc = SimpleNamespace(id=1)
        log = SimpleNamespace(id=None)
        db = FakeDb()

        documentos_repository.excluir_documento_com_log(db, doc, log)

        self.assertEqual(db.added, [log])
        self.assertEqual(db.deleted, [doc])
        self.assertTrue(db.committed)


if __name__ == "__main__":
    unittest.main()
