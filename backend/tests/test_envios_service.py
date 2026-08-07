import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.core import email_client
from app.services import envios_service


class MontarEmailFeriasTests(unittest.TestCase):
    def test_pixel_so_aparece_na_parte_html(self):
        alerta = {"ferias_usuario": "Gabriel"}

        with patch.dict("os.environ", {"PUBLIC_APP_URL": "https://rh.empresa.com"}):
            assunto, texto_plain, texto_html = envios_service.montar_email_ferias(alerta, "tok123")

        self.assertNotIn("<img", texto_plain)
        self.assertIn("<img", texto_html)
        self.assertIn("https://rh.empresa.com/api/track/tok123.png", texto_html)
        self.assertIn("Gabriel", assunto)

    def test_negrito_markdown_vira_strong_apenas_no_html(self):
        alerta = {"ferias_usuario": "Gabriel"}

        with patch.dict("os.environ", {"PUBLIC_APP_URL": "https://rh.empresa.com"}):
            _, texto_plain, texto_html = envios_service.montar_email_ferias(alerta, "tok123")

        self.assertIn("**Gabriel**", texto_plain)
        self.assertIn("<strong>Gabriel</strong>", texto_html)


class EnviarLembreteTests(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.current_user = SimpleNamespace(id=1)
        self.alerta = SimpleNamespace(id=10)
        self.alerta_dict = {
            "ferias_usuario": "Gabriel",
            "ferias_data_inicio": date(2026, 9, 14),
            "ferias_data_fim": date(2026, 9, 24),
        }
        self.configuracao = SimpleNamespace(email_destinatario="rh@empresa.com")

    def test_alerta_inexistente_retorna_404(self):
        with patch("app.services.envios_service.alertas_repository.obter_alerta_por_id", return_value=None):
            with self.assertRaises(HTTPException) as exc:
                envios_service.enviar_lembrete(self.db, 10, self.current_user)

        self.assertEqual(exc.exception.status_code, 404)

    def test_alerta_ja_possui_envio_retorna_409_sem_enviar(self):
        envio_existente = SimpleNamespace(id=99)
        with (
            patch("app.services.envios_service.alertas_repository.obter_alerta_por_id", return_value=self.alerta),
            patch(
                "app.services.envios_service.envios_repository.obter_envio_por_alerta_id",
                return_value=envio_existente,
            ),
            patch("app.services.envios_service.email_client.enviar_email_smtp") as enviar,
        ):
            with self.assertRaises(HTTPException) as exc:
                envios_service.enviar_lembrete(self.db, 10, self.current_user)

        self.assertEqual(exc.exception.status_code, 409)
        enviar.assert_not_called()

    def test_erro_smtp_vira_502_sem_gravar_nada(self):
        with (
            patch("app.services.envios_service.alertas_repository.obter_alerta_por_id", return_value=self.alerta),
            patch("app.services.envios_service.envios_repository.obter_envio_por_alerta_id", return_value=None),
            patch("app.services.envios_service.alertas_service.formatar_alerta", return_value=self.alerta_dict),
            patch(
                "app.services.envios_service.configuracao_service.obter_configuracao",
                return_value=self.configuracao,
            ),
            patch(
                "app.services.envios_service.email_client.enviar_email_smtp",
                side_effect=email_client.EmailEnvioError("falha de autenticação"),
            ),
            patch("app.services.envios_service.envios_repository.salvar") as salvar,
        ):
            with self.assertRaises(HTTPException) as exc:
                envios_service.enviar_lembrete(self.db, 10, self.current_user)

        self.assertEqual(exc.exception.status_code, 502)
        salvar.assert_not_called()

    def test_envio_bem_sucedido_fica_monitorando(self):
        with (
            patch("app.services.envios_service.alertas_repository.obter_alerta_por_id", return_value=self.alerta),
            patch("app.services.envios_service.envios_repository.obter_envio_por_alerta_id", return_value=None),
            patch("app.services.envios_service.alertas_service.formatar_alerta", return_value=self.alerta_dict),
            patch(
                "app.services.envios_service.configuracao_service.obter_configuracao",
                return_value=self.configuracao,
            ),
            patch(
                "app.services.envios_service.email_client.enviar_email_smtp",
                return_value="<msg-id@empresa.com>",
            ) as enviar,
            patch(
                "app.services.envios_service.ferias_service.calcular_dias_uteis",
                return_value=date(2026, 8, 12),
            ),
            patch("app.services.envios_service.log_service.construir_log", return_value=None),
            patch("app.services.envios_service.envios_repository.salvar") as salvar,
            patch("app.services.envios_service.envios_repository.commit") as commit,
        ):
            resultado = envios_service.enviar_lembrete(self.db, 10, self.current_user)

        enviar.assert_called_once()
        salvar.assert_called_once()
        commit.assert_called_once()

        envio_salvo = salvar.call_args[0][1]
        self.assertEqual(envio_salvo.status, "monitorando")
        self.assertEqual(envio_salvo.alerta_id, 10)
        self.assertEqual(envio_salvo.message_id, "<msg-id@empresa.com>")
        self.assertEqual(resultado["status"], "monitorando")


if __name__ == "__main__":
    unittest.main()
