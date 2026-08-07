import smtplib
import unittest
from unittest.mock import MagicMock, patch

from app.core import email_client

_ENV_CREDENCIAIS = {
    "GMAIL_USER": "lembretes@empresa.com",
    "GMAIL_APP_PASSWORD": "senha-de-app-16-digitos",
    "GMAIL_APP_PASSWORD_FILE": "",
}


class ClassificarCodigoBounceTests(unittest.TestCase):
    def test_temporarios(self):
        for codigo in ("421", "450", "451", "452", "499"):
            self.assertEqual(email_client.classificar_codigo_bounce(codigo), "temporario")

    def test_definitivos(self):
        for codigo in ("550", "551", "552", "553", "554", "599"):
            self.assertEqual(email_client.classificar_codigo_bounce(codigo), "definitivo")

    def test_desconhecido_ou_ausente(self):
        self.assertIsNone(email_client.classificar_codigo_bounce("250"))
        self.assertIsNone(email_client.classificar_codigo_bounce(None))
        self.assertIsNone(email_client.classificar_codigo_bounce(""))


class EnviarEmailSmtpTests(unittest.TestCase):
    def test_envia_com_sucesso_e_retorna_message_id(self):
        smtp_mock = MagicMock()
        with (
            patch.dict("os.environ", _ENV_CREDENCIAIS),
            patch("app.core.email_client.smtplib.SMTP_SSL", return_value=smtp_mock) as smtp_ssl,
        ):
            message_id = email_client.enviar_email_smtp(
                "destino@empresa.com", "Assunto", "texto puro", "<p>html</p>"
            )

        smtp_ssl.assert_called_once_with(
            email_client.SMTP_HOST, email_client.SMTP_PORT, timeout=email_client.CONEXAO_TIMEOUT_SEGUNDOS
        )
        smtp_mock.__enter__.return_value.login.assert_called_once_with(
            "lembretes@empresa.com", "senha-de-app-16-digitos"
        )
        smtp_mock.__enter__.return_value.send_message.assert_called_once()
        self.assertTrue(message_id.startswith("<") and message_id.endswith(">"))

    def test_sem_credenciais_nao_chama_smtp(self):
        with (
            patch.dict("os.environ", {"GMAIL_USER": "", "GMAIL_APP_PASSWORD": "", "GMAIL_APP_PASSWORD_FILE": ""}),
            patch("app.core.email_client.smtplib.SMTP_SSL") as smtp_ssl,
        ):
            with self.assertRaises(email_client.EmailEnvioError):
                email_client.enviar_email_smtp("destino@empresa.com", "Assunto", "texto", "<p>html</p>")

        smtp_ssl.assert_not_called()

    def test_falha_de_autenticacao_vira_erro_traduzido_sem_vazar_credenciais(self):
        smtp_mock = MagicMock()
        smtp_mock.__enter__.return_value.login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad credentials")

        with (
            patch.dict("os.environ", _ENV_CREDENCIAIS),
            patch("app.core.email_client.smtplib.SMTP_SSL", return_value=smtp_mock),
        ):
            with self.assertRaises(email_client.EmailEnvioError) as exc:
                email_client.enviar_email_smtp("destino@empresa.com", "Assunto", "texto", "<p>html</p>")

        mensagem = str(exc.exception)
        self.assertNotIn("senha-de-app-16-digitos", mensagem)
        self.assertNotIn("bad credentials", mensagem)


class MensagensBounceAmigaveisTests(unittest.TestCase):
    def test_todos_os_codigos_conhecidos_tem_mensagem_nao_vazia(self):
        codigos = email_client.CODIGOS_BOUNCE_TEMPORARIOS | email_client.CODIGOS_BOUNCE_DEFINITIVOS
        for codigo in codigos:
            mensagem = email_client.MENSAGENS_BOUNCE_AMIGAVEIS.get(codigo)
            self.assertIsInstance(mensagem, str)
            self.assertGreater(len(mensagem), 0)


if __name__ == "__main__":
    unittest.main()
