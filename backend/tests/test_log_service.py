import unittest
from types import SimpleNamespace

from app.services import log_service


class LogServiceTests(unittest.TestCase):
    def test_construir_log_retorna_none_para_admin_de_sistema(self):
        admin_sistema = SimpleNamespace(id=1, is_sistema=True)

        log = log_service.construir_log(admin_sistema, acao="X", detalhes="Y")

        self.assertIsNone(log)

    def test_construir_log_constroi_normalmente_para_usuario_comum(self):
        usuario = SimpleNamespace(id=7, is_sistema=False)

        log = log_service.construir_log(usuario, acao="X", detalhes="Y")

        self.assertIsNotNone(log)
        self.assertEqual(log.user_id, 7)
        self.assertEqual(log.acao, "X")
        self.assertEqual(log.detalhes, "Y")

    def test_construir_log_trata_ausencia_de_is_sistema_como_falso(self):
        usuario = SimpleNamespace(id=3)

        log = log_service.construir_log(usuario, acao="X")

        self.assertIsNotNone(log)
        self.assertEqual(log.user_id, 3)


if __name__ == "__main__":
    unittest.main()
