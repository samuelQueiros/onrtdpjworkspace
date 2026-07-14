import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import ANY, patch

from fastapi import HTTPException

from app.services import documentos_service


class DocumentosServiceTests(unittest.TestCase):
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

    def test_upload_admin_cria_somente_arquivo_enviado(self):
        admin = SimpleNamespace(id=1, nome="Administrador", role="admin")
        colaborador = SimpleNamespace(id=2, nome="Maria Silva", role="user")

        relativo, caminho_legado, caminho, copia_legada = documentos_service.salvar_arquivo_upload(
            b"%PDF-1.7", "contracheque.pdf", "application/pdf", colaborador, admin, "contracheque"
        )

        self.assertTrue(relativo.startswith("enviados/administrador/maria-silva/"))
        self.assertTrue(caminho.is_file())
        self.assertIsNone(caminho_legado)
        self.assertIsNone(copia_legada)
        self.assertEqual(list((Path(self.upload_dir.name) / "recebidos").rglob("*.*")), [])

    def test_upload_colaborador_cria_somente_arquivo_recebido(self):
        colaborador = SimpleNamespace(id=2, nome="Maria Silva", role="user")

        relativo, caminho_legado, caminho, copia_legada = documentos_service.salvar_arquivo_upload(
            b"%PDF-1.7", "atestado.pdf", "application/pdf", colaborador, colaborador, "atestado"
        )

        self.assertTrue(relativo.startswith("recebidos/maria-silva/"))
        self.assertTrue(caminho.is_file())
        self.assertIsNone(caminho_legado)
        self.assertIsNone(copia_legada)
        self.assertEqual(list((Path(self.upload_dir.name) / "enviados").rglob("*.*")), [])

    def test_atestado_de_administrador_entra_em_recebidos(self):
        admin = SimpleNamespace(id=1, nome="Catharina", role="admin")

        relativo, _, caminho, _ = documentos_service.salvar_arquivo_upload(
            b"%PDF-1.7", "atestado.pdf", "application/pdf", admin, admin, "atestado"
        )

        self.assertTrue(relativo.startswith("recebidos/catharina/"))
        self.assertTrue(caminho.is_file())

    @patch.object(documentos_service.documentos_repository, "listar_documentos_recebidos_por_administradores")
    @patch.object(documentos_service.documentos_repository, "listar_documentos_criados_por")
    def test_historico_admin_separa_atestados_e_contracheques(self, listar_criados, listar_recebidos):
        admin = SimpleNamespace(id=1, role="admin")
        listar_criados.return_value = ["contracheque"]
        listar_recebidos.return_value = ["atestado"]

        historico = documentos_service.listar_historico_documentos(SimpleNamespace(), admin)

        self.assertEqual(historico, {"recebidos": ["atestado"], "enviados": ["contracheque"]})
        listar_criados.assert_called_once_with(ANY, 1, ["contracheque", "termo_equipamentos"])

    @patch.object(documentos_service.documentos_repository, "listar_documentos_recebidos_por")
    @patch.object(documentos_service.documentos_repository, "listar_documentos_criados_por")
    def test_historico_colaborador_separa_envios_e_recebimentos(self, listar_criados, listar_recebidos):
        colaborador = SimpleNamespace(id=2, role="user")
        listar_criados.return_value = ["enviado"]
        listar_recebidos.return_value = ["recebido"]

        historico = documentos_service.listar_historico_documentos(SimpleNamespace(), colaborador)

        self.assertEqual(historico, {"recebidos": ["recebido"], "enviados": ["enviado"]})
        listar_criados.assert_called_once_with(ANY, 2, "atestado")
        listar_recebidos.assert_called_once_with(ANY, 2, 2)

    def test_admin_pode_enviar_contracheque_para_outro_usuario(self):
        admin = SimpleNamespace(id=1, role="admin")

        documentos_service.validar_permissao_upload("contracheque", 2, admin)

    def test_usuario_nao_pode_enviar_contracheque(self):
        user = SimpleNamespace(id=2, role="user")

        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_permissao_upload("contracheque", 2, user)

        self.assertEqual(exc.exception.status_code, 403)

    def test_usuario_nao_pode_enviar_documento_para_outro_usuario(self):
        user = SimpleNamespace(id=2, role="user")

        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_permissao_upload("atestado", 3, user)

        self.assertEqual(exc.exception.status_code, 403)

    def test_tipo_documento_invalido(self):
        admin = SimpleNamespace(id=1, role="admin")

        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_permissao_upload("outro", 2, admin)

        self.assertEqual(exc.exception.status_code, 400)

    def test_validar_acesso_documento_permite_dono(self):
        user = SimpleNamespace(id=2, role="user")
        doc = SimpleNamespace(user_id=2)

        documentos_service.validar_acesso_documento(doc, user)

    def test_validar_acesso_documento_bloqueia_outro_usuario(self):
        user = SimpleNamespace(id=2, role="user")
        doc = SimpleNamespace(user_id=3)

        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_acesso_documento(doc, user)

        self.assertEqual(exc.exception.status_code, 403)

    def test_validar_arquivo_upload_rejeita_tipo_nao_permitido(self):
        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_arquivo_upload(b"GIF89a", "image/gif")

        self.assertEqual(exc.exception.status_code, 400)

    def test_validar_arquivo_upload_rejeita_assinatura_invalida(self):
        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_arquivo_upload(b"nao-e-pdf", "application/pdf")

        self.assertEqual(exc.exception.status_code, 400)

    def test_validar_arquivo_upload_aceita_pdf_valido(self):
        documentos_service.validar_arquivo_upload(b"%PDF-1.7", "application/pdf")


if __name__ == "__main__":
    unittest.main()
