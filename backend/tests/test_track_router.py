import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.routers import track


class RastrearAberturaTests(unittest.TestCase):
    def test_token_existente_marca_lido_em_uma_vez(self):
        envio = SimpleNamespace(lido_em=None)
        db = MagicMock()

        with patch("app.routers.track.envios_repository.obter_envio_por_token", return_value=envio):
            response = track.rastrear_abertura("token-valido", db)

        self.assertIsNotNone(envio.lido_em)
        db.commit.assert_called_once()
        self.assertEqual(response.media_type, "image/png")
        self.assertEqual(response.body, track._PIXEL_PNG)

    def test_token_ja_lido_nao_sobrescreve_nem_commita_de_novo(self):
        primeiro_lido_em = "2026-08-01T10:00:00"
        envio = SimpleNamespace(lido_em=primeiro_lido_em)
        db = MagicMock()

        with patch("app.routers.track.envios_repository.obter_envio_por_token", return_value=envio):
            response = track.rastrear_abertura("token-ja-lido", db)

        self.assertEqual(envio.lido_em, primeiro_lido_em)
        db.commit.assert_not_called()
        self.assertEqual(response.body, track._PIXEL_PNG)

    def test_token_inexistente_ainda_retorna_o_pixel(self):
        db = MagicMock()

        with patch("app.routers.track.envios_repository.obter_envio_por_token", return_value=None):
            response = track.rastrear_abertura("token-que-nao-existe", db)

        db.commit.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.media_type, "image/png")
        self.assertEqual(response.body, track._PIXEL_PNG)


if __name__ == "__main__":
    unittest.main()
