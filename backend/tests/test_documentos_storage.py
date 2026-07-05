import os
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from fastapi import HTTPException

from app.models.documento import Documento
from app.storage import documentos_storage


class DocumentosStorageTests(unittest.TestCase):
    def setUp(self):
        self.upload_dir = tempfile.TemporaryDirectory()
        self.old_upload_dir = os.environ.get("UPLOAD_DIR")
        os.environ["UPLOAD_DIR"] = self.upload_dir.name

    def tearDown(self):
        if self.old_upload_dir is None:
            os.environ.pop("UPLOAD_DIR", None)
        else:
            os.environ["UPLOAD_DIR"] = self.old_upload_dir
        self.upload_dir.cleanup()

    def test_nome_pasta_usuario_normaliza_nome(self):
        user = SimpleNamespace(nome="Joao da Silva Junior")

        self.assertEqual(documentos_storage.nome_pasta_usuario(user), "joao-da-silva-junior")

    def test_nome_pasta_usuario_tem_fallback(self):
        user = SimpleNamespace(nome="!!!")

        self.assertEqual(documentos_storage.nome_pasta_usuario(user), "usuario")

    def test_validar_assinatura_arquivo_permite_tipos_esperados(self):
        self.assertTrue(documentos_storage.validar_assinatura_arquivo(b"%PDF-1.7", "application/pdf"))
        self.assertTrue(documentos_storage.validar_assinatura_arquivo(b"\xff\xd8\xff\xe0", "image/jpeg"))
        self.assertTrue(documentos_storage.validar_assinatura_arquivo(b"\x89PNG\r\n\x1a\n", "image/png"))

    def test_validar_assinatura_arquivo_recusa_conteudo_invalido(self):
        self.assertFalse(documentos_storage.validar_assinatura_arquivo(b"<script></script>", "application/pdf"))
        self.assertFalse(documentos_storage.validar_assinatura_arquivo(b"GIF89a", "image/png"))

    def test_gerar_nome_armazenamento_remove_caminho_e_normaliza(self):
        nome = documentos_storage.gerar_nome_armazenamento("../Contra Cheque 07.pdf", "application/pdf")

        self.assertRegex(nome, r"^[0-9a-f]{32}-contra-cheque-07\.pdf$")

    def test_gerar_nome_armazenamento_corrige_extensao_pelo_mime(self):
        nome = documentos_storage.gerar_nome_armazenamento("foto.exe", "image/png")

        self.assertRegex(nome, r"^[0-9a-f]{32}-foto\.png$")

    def test_obter_upload_dir_cria_pastas_base(self):
        upload_dir = documentos_storage.obter_upload_dir()

        self.assertTrue((upload_dir / "enviados").is_dir())
        self.assertTrue((upload_dir / "recebidos").is_dir())

    def test_caminho_documento_rejeita_path_traversal(self):
        doc = Documento(caminho_arquivo="../segredo.pdf")

        with self.assertRaises(HTTPException) as exc:
            documentos_storage.caminho_documento(doc)

        self.assertEqual(exc.exception.status_code, 400)

    def test_caminho_documento_retorna_arquivo_dentro_do_upload_dir(self):
        upload_dir = Path(self.upload_dir.name)
        caminho = upload_dir / "recebidos" / "gabriel" / "arquivo.pdf"
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_bytes(b"%PDF-1.7")

        doc = Documento(caminho_arquivo="recebidos/gabriel/arquivo.pdf")

        self.assertEqual(documentos_storage.caminho_documento(doc), caminho.resolve())

    def test_content_disposition_remove_quebra_de_linha(self):
        header = documentos_storage.content_disposition("attachment", "arquivo\r\nmalicioso.pdf")

        self.assertNotIn("\r", header)
        self.assertNotIn("\n", header)
        self.assertTrue(header.startswith("attachment;"))


if __name__ == "__main__":
    unittest.main()
