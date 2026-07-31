import unittest

from app.core.cpf import formatar_cpf, mascarar_cpf, normalizar_cpf, validar_cpf


class CpfTests(unittest.TestCase):
    def test_normaliza_pontuacao_e_espacos(self):
        self.assertEqual(normalizar_cpf(" 529.982.247-25 "), "52998224725")

    def test_valida_cpf_e_retorna_apenas_digitos(self):
        self.assertEqual(validar_cpf("529.982.247-25"), "52998224725")

    def test_rejeita_digitos_verificadores_invalidos(self):
        with self.assertRaisesRegex(ValueError, "CPF inválido"):
            validar_cpf("529.982.247-24")

    def test_rejeita_sequencia_repetida(self):
        with self.assertRaisesRegex(ValueError, "CPF inválido"):
            validar_cpf("111.111.111-11")

    def test_rejeita_letras_e_caracteres_fora_do_formato(self):
        for valor in ("abc529.982.247-25", "529.982.247-25x", "529/982/247-25"):
            with self.subTest(valor=valor):
                with self.assertRaisesRegex(ValueError, "CPF inválido"):
                    validar_cpf(valor)

    def test_formata_cpf_normalizado(self):
        self.assertEqual(formatar_cpf("52998224725"), "529.982.247-25")

    def test_mascara_cpf_sem_expor_nove_primeiros_digitos(self):
        self.assertEqual(mascarar_cpf("529.982.247-25"), "***.***.***-25")

    def test_mascara_valor_incompleto_de_forma_segura(self):
        self.assertEqual(mascarar_cpf("123"), "***.***.***-**")
        self.assertIsNone(mascarar_cpf(None))


if __name__ == "__main__":
    unittest.main()
