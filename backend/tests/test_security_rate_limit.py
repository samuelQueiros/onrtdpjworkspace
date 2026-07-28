import unittest
import os
from types import SimpleNamespace

from fastapi import HTTPException

from app.core.security import (
    LOGIN_MAX_ATTEMPTS,
    limpar_falhas_login,
    registrar_falha_login,
    obter_ip_cliente,
    verificar_limite_login,
)


class SecurityRateLimitTests(unittest.TestCase):
    def test_ip_encaminhado_so_e_aceito_de_proxy_confiavel(self):
        request = SimpleNamespace(
            client=SimpleNamespace(host="172.20.0.5"),
            headers={"x-forwarded-for": "203.0.113.10, 172.20.0.5"},
        )
        anterior = os.environ.get("TRUSTED_PROXY_IPS")
        os.environ["TRUSTED_PROXY_IPS"] = "172.20.0.0/16"
        try:
            self.assertEqual(obter_ip_cliente(request), "203.0.113.10")
            os.environ["TRUSTED_PROXY_IPS"] = ""
            self.assertEqual(obter_ip_cliente(request), "172.20.0.5")
        finally:
            if anterior is None:
                os.environ.pop("TRUSTED_PROXY_IPS", None)
            else:
                os.environ["TRUSTED_PROXY_IPS"] = anterior

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
