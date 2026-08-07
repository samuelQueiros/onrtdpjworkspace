import unittest
from email.message import EmailMessage

from app.core import email_parsing


class RemoverCitacaoTests(unittest.TestCase):
    def test_corta_em_escreveu_gmail_ptbr(self):
        texto = (
            "Ok, pode prosseguir.\n\n"
            "Em qua., 7 de ago. de 2026 às 10:00, RH <rh@empresa.com> escreveu:\n"
            "> texto original citado"
        )
        self.assertEqual(email_parsing.remover_citacao(texto), "Ok, pode prosseguir.")

    def test_corta_on_wrote_gmail_en(self):
        texto = (
            "Sure, go ahead.\n\n"
            "On Wed, Aug 7, 2026 at 10:00 AM RH <rh@empresa.com> wrote:\n"
            "> original quoted text"
        )
        self.assertEqual(email_parsing.remover_citacao(texto), "Sure, go ahead.")

    def test_corta_bloco_outlook(self):
        texto = (
            "Aprovado, pode seguir.\n\n"
            "De: RH <rh@empresa.com>\n"
            "Enviado: quarta-feira, 7 de agosto de 2026 10:00\n"
            "Para: Colaborador <colaborador@empresa.com>\n"
            "Assunto: Aviso de férias\n\n"
            "Texto original aqui."
        )
        self.assertEqual(email_parsing.remover_citacao(texto), "Aprovado, pode seguir.")

    def test_corta_linhas_iniciadas_com_maior_que(self):
        texto = "Confirmado.\n> texto citado\n> mais texto citado"
        self.assertEqual(email_parsing.remover_citacao(texto), "Confirmado.")

    def test_mantem_texto_sem_citacao(self):
        texto = "Só confirmando o recebimento, obrigado."
        self.assertEqual(email_parsing.remover_citacao(texto), texto)


class ExtrairTextoPuroTests(unittest.TestCase):
    def test_prefere_text_plain_quando_multipart(self):
        msg = EmailMessage()
        msg.set_content("texto puro")
        msg.add_alternative("<p>texto <b>html</b></p>", subtype="html")

        self.assertEqual(email_parsing.extrair_texto_puro(msg).strip(), "texto puro")

    def test_cai_para_html_stripado_quando_so_ha_html_multipart(self):
        msg = EmailMessage()
        msg.make_mixed()
        parte_html = EmailMessage()
        parte_html.set_content("<p>Apenas <b>HTML</b> aqui</p>", subtype="html")
        msg.attach(parte_html)

        resultado = email_parsing.extrair_texto_puro(msg)

        self.assertIn("Apenas", resultado)
        self.assertIn("HTML", resultado)
        self.assertNotIn("<p>", resultado)
        self.assertNotIn("<b>", resultado)

    def test_cai_para_html_stripado_quando_mensagem_de_parte_unica(self):
        msg = EmailMessage()
        msg.set_content("<p>Só <b>HTML</b> de parte única</p>", subtype="html")

        resultado = email_parsing.extrair_texto_puro(msg)

        self.assertIn("única", resultado)
        self.assertNotIn("<p>", resultado)


class PrepararRespostaTests(unittest.TestCase):
    def test_remove_citacao_e_trunca_ambos_os_campos(self):
        msg = EmailMessage()
        msg.set_content(
            "Aprovado.\n\nEm qua., 7 de ago. de 2026 às 10:00, RH <rh@empresa.com> escreveu:\n> original"
        )

        limpo, bruto = email_parsing.preparar_resposta(msg)

        self.assertEqual(limpo, "Aprovado.")
        self.assertIn("original", bruto)


class InterpretarBounceTests(unittest.TestCase):
    def _montar_dsn(self, codigo_smtp: str, references: str) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = "Mail Delivery Subsystem <mailer-daemon@googlemail.com>"
        msg["References"] = references
        msg.make_mixed()

        relatorio = EmailMessage()
        relatorio.set_content(
            f"Reporting-MTA: dns; example.com\nDiagnostic-Code: smtp; {codigo_smtp} falha na entrega\n"
        )
        msg.attach(relatorio)
        return msg

    def test_extrai_codigo_definitivo_e_referencia(self):
        dsn = self._montar_dsn("550", "<abc123@empresa.com>")

        info = email_parsing.interpretar_bounce(dsn)

        self.assertIsNotNone(info)
        self.assertEqual(info["codigo"], "550")
        self.assertEqual(info["message_id_referenciado"], "<abc123@empresa.com>")

    def test_extrai_codigo_temporario(self):
        dsn = self._montar_dsn("451", "<abc123@empresa.com>")

        info = email_parsing.interpretar_bounce(dsn)

        self.assertEqual(info["codigo"], "451")

    def test_retorna_none_quando_nao_ha_codigo_smtp(self):
        msg = EmailMessage()
        msg.set_content("Mensagem qualquer sem status de entrega.")

        self.assertIsNone(email_parsing.interpretar_bounce(msg))


if __name__ == "__main__":
    unittest.main()
