import hashlib
import html as html_module
import os
import re
import sys
import tempfile
import types
import unittest
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.services import termos_equipamentos_service
from app.storage.termos_storage import salvar_termo_pdf


class TermosEquipamentosTests(unittest.TestCase):
    @staticmethod
    def solicitacao(nome: str = "Maria da Silva") -> SimpleNamespace:
        momento = datetime(2026, 7, 13, 15, 30, tzinfo=UTC)
        item = SimpleNamespace(
            id=1,
            status_item="entregue",
            tipo_snapshot="notebook",
            marca_modelo_snapshot="Dell Latitude 5450",
            estado_conservacao_snapshot="Novo, sem avarias",
            numero_patrimonio_snapshot="PAT-001",
            numero_serie_snapshot="SERIE-001",
            observacoes_snapshot="Carregador incluso",
        )
        return SimpleNamespace(
            id=123,
            termo_versao=None,
            aceite_declaracao=True,
            itens=[item],
            nome_colaborador_snapshot=nome,
            cargo_snapshot="Analista",
            departamento_snapshot="Administrativo",
            responsavel_entrega_nome="Administrador",
            responsavel_entrega_cargo="Gerente",
            local_entrega="Brasilia/DF",
            local_aceite="Brasilia/DF",
            aceito_em=momento,
            criado_em=momento,
            entregue_em=momento,
            aceite_ip="127.0.0.1",
            aceite_request_id="req-123",
            observacoes="Uso em home office",
            termo_html_snapshot_criptografado=None,
        )

    def test_metadados_preservam_versao_hash_e_clausulas_criticas(self):
        metadados = termos_equipamentos_service.obter_metadados_versao()

        self.assertEqual(metadados["codigo"], "v2")
        self.assertEqual(len(metadados["conteudo_hash"]), 64)
        self.assertIn(
            "Desconto em folha de pagamento, desde que previamente autorizado",
            metadados["clausulas"],
        )
        self.assertIn(
            "A ocorrência de furto ou roubo não implicará responsabilização automática",
            metadados["clausulas"],
        )
        self.assertIn(
            "Antes da aplicação de qualquer cobrança ou penalidade",
            metadados["clausulas"],
        )

    def test_todas_as_clausulas_versionadas_estao_no_template_pdf(self):
        template = termos_equipamentos_service.obter_conteudo_template()
        texto_visivel = html_module.unescape(re.sub(r"<[^>]+>", " ", template))
        texto_visivel = " ".join(texto_visivel.split()).casefold()

        for linha in termos_equipamentos_service.obter_clausulas_termo().splitlines():
            clausula = re.sub(r"^\d+\.\s*", "", linha).strip()
            if clausula:
                self.assertIn(" ".join(clausula.split()).casefold(), texto_visivel)

    def test_hash_canoniza_quebras_de_linha_e_inclui_logo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            template = Path(temp_dir) / "v1.html"
            logo = Path(temp_dir) / "logo.png"
            template.write_bytes(b"linha 1\r\nlinha 2\r\n")
            logo.write_bytes(b"logo-a")

            with (
                patch.object(termos_equipamentos_service, "TEMPLATE_PATH", template),
                patch.object(termos_equipamentos_service, "LOGO_PATH", logo),
            ):
                hash_crlf = termos_equipamentos_service.obter_hash_template()
                template.write_bytes(b"linha 1\nlinha 2\n")
                hash_lf = termos_equipamentos_service.obter_hash_template()
                logo.write_bytes(b"logo-b")
                hash_novo_logo = termos_equipamentos_service.obter_hash_template()

        self.assertEqual(hash_crlf, hash_lf)
        self.assertNotEqual(hash_lf, hash_novo_logo)

    def test_html_usa_snapshots_e_escapa_dados(self):
        html = termos_equipamentos_service.renderizar_termo_html(
            self.solicitacao("Maria <script>alert(1)</script>"),
            "52998224725",
        )

        self.assertIn("Maria &lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("Maria <script>", html)
        self.assertIn("Dell Latitude 5450", html)
        self.assertIn("529.982.247-25", html)
        self.assertIn("req-123", html)

    def test_geracao_calcula_hash_e_nome_previsivel(self):
        pdf = b"%PDF-1.7\ntermo-controlado"

        class FakeHTML:
            def __init__(self, *, string):
                self.string = string

            def write_pdf(self):
                return pdf

        modulo = types.ModuleType("weasyprint")
        modulo.HTML = FakeHTML
        with patch.dict(sys.modules, {"weasyprint": modulo}):
            termo = termos_equipamentos_service.gerar_termo_pdf(
                self.solicitacao(),
                "52998224725",
            )

        self.assertEqual(termo.pdf_bytes, pdf)
        self.assertEqual(termo.pdf_hash, hashlib.sha256(pdf).hexdigest())
        self.assertEqual(
            termo.nome_arquivo,
            "termo-equipamentos-maria-da-silva-solicitacao-123-v2.pdf",
        )

    def test_layout_v2_mantem_identificacao_e_assinaturas_em_larguras_legiveis(self):
        from weasyprint import HTML

        html = termos_equipamentos_service.renderizar_termo_html(
            self.solicitacao(),
            "52998224725",
        )
        documento = HTML(string=html).render()
        caixas = [caixa for pagina in documento.pages for caixa in pagina._page_box.descendants()]

        def maior_caixa(classe):
            candidatas = [
                caixa
                for caixa in caixas
                if caixa.element is not None
                and classe in (caixa.element.get("class") or "").split()
            ]
            return max(candidatas, key=lambda caixa: caixa.width)

        identificacao = maior_caixa("identity-grid")
        assinaturas = maior_caixa("signature-grid")

        self.assertGreater(identificacao.width, 600)
        self.assertGreater(assinaturas.width, 600)
        self.assertGreater(min(filho.width for filho in identificacao.children), 300)
        self.assertGreater(min(filho.width for filho in assinaturas.children), 290)

    def test_regeneracao_descriptografa_snapshot_html_historico(self):
        pdf = b"%PDF-1.7\nsnapshot-historico"
        html_historico = "<html><body>Termo aceito</body></html>"
        solicitacao = self.solicitacao()
        solicitacao.termo_html_snapshot_criptografado = "sensitive:token-cifrado"
        solicitacao.termo_versao = SimpleNamespace(codigo="v1", conteudo_hash="a" * 64)

        class FakeHTML:
            def __init__(self, *, string):
                self.string = string

            def write_pdf(self):
                self.assert_html_historico()
                return pdf

            def assert_html_historico(self):
                if self.string != html_historico:
                    raise AssertionError("A regeneracao nao usou o HTML historico")

        modulo = types.ModuleType("weasyprint")
        modulo.HTML = FakeHTML
        with (
            patch.dict(sys.modules, {"weasyprint": modulo}),
            patch.object(
                termos_equipamentos_service,
                "descriptografar_dado_sensivel",
                return_value=html_historico,
            ) as descriptografar,
        ):
            termo = termos_equipamentos_service.gerar_pdf_snapshot(solicitacao)

        descriptografar.assert_called_once_with("sensitive:token-cifrado")
        self.assertEqual(termo.html, html_historico)
        self.assertEqual(termo.pdf_bytes, pdf)
        self.assertEqual(termo.conteudo_hash, "a" * 64)

    def test_storage_e_atomico_e_idempotente(self):
        pdf = b"%PDF-1.7\nconteudo-idempotente"
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {"UPLOAD_DIR": temp_dir},
            clear=False,
        ):
            primeiro = salvar_termo_pdf(pdf, "Maria da Silva", 123, "v1")
            mtime = primeiro.caminho_absoluto.stat().st_mtime_ns
            segundo = salvar_termo_pdf(pdf, "Maria da Silva", 123, "v1")

            self.assertEqual(primeiro.caminho_relativo, segundo.caminho_relativo)
            self.assertEqual(primeiro.pdf_hash, segundo.pdf_hash)
            self.assertEqual(mtime, segundo.caminho_absoluto.stat().st_mtime_ns)
            self.assertEqual(list(segundo.caminho_absoluto.parent.glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
