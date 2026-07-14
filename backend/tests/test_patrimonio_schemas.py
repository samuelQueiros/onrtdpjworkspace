import unittest

from pydantic import ValidationError

from app.schemas.patrimonio import (
    AceiteSolicitacaoCreate,
    AprovacaoSolicitacaoCreate,
    DevolucaoSolicitacaoCreate,
    EntregaSolicitacaoCreate,
    EquipamentoUpdate,
    SolicitacaoEquipamentoCreate,
    VinculoCreate,
)


class PatrimonioSchemasTests(unittest.TestCase):
    def test_edicao_rejeita_nulo_em_campo_obrigatorio_do_equipamento(self):
        with self.assertRaises(ValidationError):
            EquipamentoUpdate(modelo=None)

    def test_solicitacao_rejeita_equipamentos_repetidos(self):
        with self.assertRaises(ValidationError):
            SolicitacaoEquipamentoCreate(
                tipo_solicitacao="item_diferente", equipamento_ids=[10, 10]
            )

    def test_aprovacao_rejeita_itens_repetidos(self):
        with self.assertRaises(ValidationError):
            AprovacaoSolicitacaoCreate(item_ids_aprovados=[101, 101])

    def test_segunda_maquina_exige_justificativa_na_vinculacao(self):
        with self.assertRaises(ValidationError):
            VinculoCreate(user_id=2, permitir_segunda_maquina=True)

    def test_entrega_rejeita_item_repetido(self):
        with self.assertRaises(ValidationError):
            EntregaSolicitacaoCreate(
                responsavel_entrega_nome="Administrador",
                responsavel_entrega_cargo="Gerente",
                local_entrega="Escritorio",
                itens=[
                    {"item_id": 101, "estado_conservacao": "Bom"},
                    {"item_id": 101, "estado_conservacao": "Bom"},
                ],
            )

    def test_aceite_exige_confirmacao_explicita(self):
        with self.assertRaises(ValidationError):
            AceiteSolicitacaoCreate(declaracao_aceite=False, local_aceite="Brasilia")

    def test_devolucao_de_item_presente_exige_estado_conservacao(self):
        with self.assertRaises(ValidationError):
            DevolucaoSolicitacaoCreate(
                itens=[{"item_id": 101, "situacao": "devolvido"}],
                estado_conservacao_geral="Bom",
            )

    def test_devolucao_rejeita_item_repetido(self):
        with self.assertRaises(ValidationError):
            DevolucaoSolicitacaoCreate(
                itens=[
                    {"item_id": 101, "situacao": "ausente"},
                    {"item_id": 101, "situacao": "ausente"},
                ],
                estado_conservacao_geral="Conferido",
            )


if __name__ == "__main__":
    unittest.main()
