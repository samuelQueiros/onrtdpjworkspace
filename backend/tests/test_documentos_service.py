import unittest
from types import SimpleNamespace

from fastapi import HTTPException

from app.services import documentos_service


class DocumentosServiceTests(unittest.TestCase):
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
