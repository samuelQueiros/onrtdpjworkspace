import unittest

from fastapi import HTTPException

from app.core.security import (
    LOGIN_MAX_ATTEMPTS,
    limpar_falhas_login,
    registrar_falha_login,
    verificar_limite_login,
)


class SecurityRateLimitTests(unittest.TestCase):
    def test_limite_e_isolado_por_ip_e_email(self):
        chave = "127.0.0.1|teste@sistema.com"
        outra = "127.0.0.1|outra@sistema.com"
        try:
            for _ in range(LOGIN_MAX_ATTEMPTS):
                registrar_falha_login(chave)
            with self.assertRaises(HTTPException) as exc:
                verificar_limite_login(chave)
            self.assertEqual(exc.exception.status_code, 429)
            verificar_limite_login(outra)
        finally:
            limpar_falhas_login(chave)
            limpar_falhas_login(outra)


if __name__ == "__main__":
    unittest.main()
