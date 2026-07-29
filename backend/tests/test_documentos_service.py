import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.services import documentos_service


class DocumentosServiceTests(unittest.TestCase):
    PDF_VALIDO = b"%PDF-1.7\n%%EOF"

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

    def test_upload_admin_cria_arquivos_recebido_e_enviado(self):
        admin = SimpleNamespace(id=1, nome="Administrador", role="admin")
        colaborador = SimpleNamespace(id=2, nome="Maria Silva", role="user")

        relativo, caminho_enviado_relativo, caminho, caminho_enviado = documentos_service.salvar_arquivo_upload(
            self.PDF_VALIDO, "contracheque.pdf", "application/pdf", colaborador, admin, "usuario"
        )

        self.assertTrue(relativo.startswith("recebidos/maria-silva/"))
        self.assertTrue(caminho.is_file())
        self.assertTrue(caminho_enviado_relativo.startswith("enviados/administrador/maria-silva/"))
        self.assertTrue(caminho_enviado.is_file())
        self.assertEqual(caminho.read_bytes(), caminho_enviado.read_bytes())

    def test_upload_atestado_admin_para_colaborador_segue_fluxo_de_enviados(self):
        admin = SimpleNamespace(id=1, nome="Administrador", role="admin")
        colaborador = SimpleNamespace(id=2, nome="Maria Silva", role="user")

        relativo, caminho_enviado_relativo, caminho, caminho_enviado = documentos_service.salvar_arquivo_upload(
            self.PDF_VALIDO, "atestado.pdf", "application/pdf", colaborador, admin, "usuario"
        )

        self.assertTrue(relativo.startswith("recebidos/maria-silva/"))
        self.assertTrue(caminho_enviado_relativo.startswith("enviados/administrador/maria-silva/"))
        self.assertTrue(caminho.is_file())
        self.assertTrue(caminho_enviado.is_file())

    def test_upload_colaborador_cria_arquivos_recebido_e_enviado_para_administracao(self):
        colaborador = SimpleNamespace(id=2, nome="Maria Silva", role="user")

        relativo, caminho_enviado_relativo, caminho, caminho_enviado = documentos_service.salvar_arquivo_upload(
            self.PDF_VALIDO, "atestado.pdf", "application/pdf", colaborador, colaborador, "administracao"
        )

        self.assertTrue(relativo.startswith("recebidos/administracao/maria-silva/"))
        self.assertTrue(caminho.is_file())
        self.assertTrue(caminho_enviado_relativo.startswith("enviados/maria-silva/administracao/"))
        self.assertTrue(caminho_enviado.is_file())
        self.assertEqual(caminho.read_bytes(), caminho_enviado.read_bytes())

    def test_documento_de_administrador_para_si_mesmo_entra_em_recebidos_pessoais(self):
        admin = SimpleNamespace(id=1, nome="Catharina", role="admin")

        relativo, _, caminho, _ = documentos_service.salvar_arquivo_upload(
            self.PDF_VALIDO, "atestado.pdf", "application/pdf", admin, admin, "usuario"
        )

        self.assertTrue(relativo.startswith("recebidos/catharina/"))
        self.assertTrue(caminho.is_file())

    @patch.object(documentos_service.documentos_repository, "listar_historico_paginado")
    @patch.object(documentos_service.documentos_repository, "contar_historico")
    def test_historico_admin_pagina_e_filtra_caixa(self, contar, listar):
        admin = SimpleNamespace(id=1, role="admin")
        contar.return_value = 21
        listar.return_value = ["documento"]

        db = SimpleNamespace()
        historico = documentos_service.listar_historico_documentos_paginado(
            db,
            admin,
            caixa="recebidos_administracao",
            page=2,
            page_size=10,
            user_id=4,
        )

        self.assertEqual(
            historico,
            {
                "items": ["documento"],
                "total": 21,
                "page": 2,
                "page_size": 10,
                "pages": 3,
            },
        )
        contar.assert_called_once_with(db, "recebidos_administracao", 1, 4)
        listar.assert_called_once_with(db, "recebidos_administracao", 1, 4, 10, 10)

    @patch.object(documentos_service.documentos_repository, "listar_historico_paginado")
    @patch.object(documentos_service.documentos_repository, "contar_historico")
    def test_historico_colaborador_lista_caixa_pessoal(self, contar, listar):
        colaborador = SimpleNamespace(id=2, role="user")
        contar.return_value = 0
        listar.return_value = []

        db = SimpleNamespace()
        historico = documentos_service.listar_historico_documentos_paginado(
            db,
            colaborador,
            caixa="recebidos_pessoais",
            page=1,
            page_size=10,
        )

        self.assertEqual(historico["pages"], 1)
        contar.assert_called_once_with(db, "recebidos_pessoais", 2, None)
        listar.assert_called_once_with(db, "recebidos_pessoais", 2, None, 0, 10)

    def test_historico_bloqueia_caixa_administrativa_para_colaborador(self):
        colaborador = SimpleNamespace(id=2, role="user")

        with self.assertRaises(HTTPException) as exc:
            documentos_service.listar_historico_documentos_paginado(
                SimpleNamespace(),
                colaborador,
                caixa="recebidos_administracao",
                page=1,
                page_size=10,
            )

        self.assertEqual(exc.exception.status_code, 403)

    def test_historico_bloqueia_filtro_de_usuario_para_colaborador(self):
        colaborador = SimpleNamespace(id=2, role="user")

        with self.assertRaises(HTTPException) as exc:
            documentos_service.listar_historico_documentos_paginado(
                SimpleNamespace(),
                colaborador,
                caixa="enviados",
                page=1,
                page_size=10,
                user_id=3,
            )

        self.assertEqual(exc.exception.status_code, 403)

    def test_admin_pode_enviar_contracheque_para_outro_usuario(self):
        admin = SimpleNamespace(id=1, role="admin")

        documentos_service.validar_permissao_upload("contracheque", 2, "usuario", admin)

    def test_usuario_nao_pode_enviar_contracheque(self):
        user = SimpleNamespace(id=2, role="user")

        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_permissao_upload("contracheque", 2, "administracao", user)

        self.assertEqual(exc.exception.status_code, 403)

    def test_usuario_nao_pode_enviar_documento_para_outro_usuario(self):
        user = SimpleNamespace(id=2, role="user")

        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_permissao_upload("atestado", 3, "usuario", user)

        self.assertEqual(exc.exception.status_code, 403)

    def test_tipo_documento_invalido(self):
        admin = SimpleNamespace(id=1, role="admin")

        with self.assertRaises(HTTPException) as exc:
            documentos_service.validar_permissao_upload("invalido", 2, "usuario", admin)

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
        documentos_service.validar_arquivo_upload(self.PDF_VALIDO, "application/pdf")

    def test_normalizar_observacao_remove_espacos(self):
        self.assertEqual(
            documentos_service.normalizar_observacao("  Documento referente a julho.  "),
            "Documento referente a julho.",
        )

    def test_normalizar_observacao_vazia_retorna_none(self):
        self.assertIsNone(documentos_service.normalizar_observacao("   "))

    def test_normalizar_observacao_rejeita_limite_excedido(self):
        with self.assertRaises(HTTPException) as exc:
            documentos_service.normalizar_observacao(
                "x" * (documentos_service.MAX_OBSERVACAO_LENGTH + 1)
            )

        self.assertEqual(exc.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
