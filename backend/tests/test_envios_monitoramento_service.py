import unittest
from datetime import datetime, timedelta
from email.message import EmailMessage
from unittest.mock import MagicMock, patch

from app.core.timezone import FUSO_SAO_PAULO
from app.models.envio import Envio
from app.services import envios_monitoramento_service as monitoramento


def _fazer_envio(**kwargs) -> Envio:
    padrao = dict(
        id=1,
        status="monitorando",
        message_id="<msg-1@empresa.com>",
        tentativas_verificacao=0,
        enviado_em=datetime.now(FUSO_SAO_PAULO) - timedelta(hours=1),
        prazo_limite=datetime.now(FUSO_SAO_PAULO) + timedelta(days=1),
    )
    padrao.update(kwargs)
    return Envio(**padrao)


def _bounce(de: str, references: str, diagnostico: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = de
    msg["References"] = references
    msg.make_mixed()
    relatorio = EmailMessage()
    relatorio.set_content(f"Diagnostic-Code: smtp; {diagnostico}\n")
    msg.attach(relatorio)
    return msg


def _resposta(de: str, in_reply_to: str, corpo: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = de
    msg["In-Reply-To"] = in_reply_to
    msg.set_content(corpo)
    return msg


class ProcessarCicloTests(unittest.TestCase):
    def test_prazo_estourado_marca_sem_retorno_sem_tocar_imap(self):
        envio = _fazer_envio(prazo_limite=datetime.now(FUSO_SAO_PAULO) - timedelta(minutes=1))
        db = MagicMock()

        with (
            patch(
                "app.services.envios_monitoramento_service.envios_repository.listar_envios_monitorando",
                return_value=[envio],
            ),
            patch("app.services.envios_monitoramento_service.email_client.conectar_imap") as conectar,
        ):
            monitoramento._processar_ciclo(db)

        conectar.assert_not_called()
        self.assertEqual(envio.status, "sem_retorno")
        self.assertEqual(len(envio.eventos), 1)
        self.assertEqual(envio.eventos[0].tipo, "prazo_estourado")

    def test_bounce_temporario_incrementa_tentativas_mantem_monitorando(self):
        envio = _fazer_envio()
        mensagem = _bounce(
            "Mail Delivery Subsystem <mailer-daemon@googlemail.com>",
            envio.message_id,
            "451 tente novamente mais tarde",
        )
        self._executar_ciclo_com_mensagens(envio, [mensagem])

        self.assertEqual(envio.status, "monitorando")
        self.assertEqual(envio.tentativas_verificacao, 1)
        self.assertEqual(envio.eventos[-1].tipo, "bounce_temporario")

    def test_bounce_definitivo_marca_erro_definitivo_com_mensagem_amigavel(self):
        envio = _fazer_envio()
        mensagem = _bounce(
            "Mail Delivery Subsystem <mailer-daemon@googlemail.com>",
            envio.message_id,
            "550 endereço inexistente",
        )
        self._executar_ciclo_com_mensagens(envio, [mensagem])

        self.assertEqual(envio.status, "erro_definitivo")
        self.assertEqual(envio.erro_codigo, "550")
        self.assertTrue(envio.erro_mensagem)
        self.assertNotIn("Traceback", envio.erro_mensagem)
        self.assertEqual(envio.eventos[-1].tipo, "bounce_definitivo")

    def test_resposta_detectada_marca_respondido_sem_a_citacao(self):
        envio = _fazer_envio()
        corpo = "Aprovado, pode seguir.\n\nEm qua., 7 de ago. de 2026, RH <rh@empresa.com> escreveu:\n> original"
        mensagem = _resposta("RH <rh@empresa.com>", envio.message_id, corpo)
        self._executar_ciclo_com_mensagens(envio, [mensagem])

        self.assertEqual(envio.status, "respondido")
        self.assertEqual(envio.resposta_texto, "Aprovado, pode seguir.")
        self.assertIn("original", envio.resposta_bruta)
        self.assertIsNotNone(envio.respondido_em)
        self.assertEqual(envio.eventos[-1].tipo, "resposta_detectada")

    def test_mensagem_nao_relacionada_e_ignorada(self):
        envio = _fazer_envio()
        mensagem = _resposta("Outra Pessoa <outra@empresa.com>", "<outro-message-id@empresa.com>", "Assunto qualquer")
        self._executar_ciclo_com_mensagens(envio, [mensagem])

        self.assertEqual(envio.status, "monitorando")
        self.assertEqual(envio.tentativas_verificacao, 0)
        self.assertIsNotNone(envio.ultima_verificacao_em)

    def _executar_ciclo_com_mensagens(self, envio: Envio, mensagens: list) -> None:
        db = MagicMock()
        with (
            patch(
                "app.services.envios_monitoramento_service.envios_repository.listar_envios_monitorando",
                return_value=[envio],
            ),
            patch("app.services.envios_monitoramento_service.email_client.conectar_imap") as conectar,
            patch(
                "app.services.envios_monitoramento_service._buscar_mensagens_recentes",
                return_value=mensagens,
            ),
        ):
            conectar.return_value.__enter__.return_value = MagicMock()
            monitoramento._processar_ciclo(db)


class ExecutarCicloMonitoramentoTests(unittest.TestCase):
    def test_pula_ciclo_quando_lock_ja_esta_ocupado(self):
        db = MagicMock()
        db.bind.dialect.name = "postgresql"
        db.execute.return_value.scalar.return_value = False

        with patch(
            "app.services.envios_monitoramento_service.envios_repository.listar_envios_monitorando"
        ) as listar:
            monitoramento.executar_ciclo_monitoramento(db)

        listar.assert_not_called()

    def test_processa_e_libera_lock_quando_obtido(self):
        db = MagicMock()
        db.bind.dialect.name = "postgresql"
        db.execute.return_value.scalar.return_value = True

        with patch(
            "app.services.envios_monitoramento_service.envios_repository.listar_envios_monitorando",
            return_value=[],
        ) as listar:
            monitoramento.executar_ciclo_monitoramento(db)

        listar.assert_called_once()
        # 1a chamada = pg_try_advisory_lock, 2a chamada (no finally) = pg_advisory_unlock
        self.assertEqual(db.execute.call_count, 2)


if __name__ == "__main__":
    unittest.main()
