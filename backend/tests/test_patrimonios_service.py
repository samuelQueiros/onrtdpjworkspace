import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.schemas.patrimonio import (
    BaixaCreate,
    EquipamentoCreate,
    EquipamentoUpdate,
    ManutencaoCreate,
    VinculoCreate,
)
from app.services import patrimonios_service


class FakeDb:
    def __init__(self):
        self.rollback_called = False
        self.refreshed = []

    def rollback(self):
        self.rollback_called = True

    def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = 101
        self.refreshed.append(obj)


def equipamento(**alteracoes):
    dados = {
        "id": 10,
        "numero_patrimonio": "PAT-10",
        "numero_serie": "SER-10",
        "tipo": "notebook",
        "marca": "Dell",
        "modelo": "Latitude",
        "descricao": "Equipamento de teste",
        "estado_conservacao": "Bom",
        "status": "disponivel",
        "ativo": True,
        "vinculos": [],
        "eventos": [],
        "criado_em": None,
        "atualizado_em": None,
    }
    dados.update(alteracoes)
    return SimpleNamespace(**dados)


class PatrimoniosServiceTests(unittest.TestCase):
    def setUp(self):
        self.admin = SimpleNamespace(id=1, nome="Administrador", role="admin")

    def test_buscar_equipamento_retorna_404_quando_inexistente(self):
        with patch(
            "app.services.patrimonios_service.patrimonios_repository.obter_equipamento",
            return_value=None,
        ):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.buscar_equipamento(SimpleNamespace(), 999)

        self.assertEqual(exc.exception.status_code, 404)

    def test_criar_equipamento_rejeita_numero_de_patrimonio_duplicado(self):
        payload = EquipamentoCreate(
            numero_patrimonio="PAT-10",
            numero_serie="SER-11",
            tipo="notebook",
            marca="Dell",
            modelo="Latitude",
            estado_conservacao="Bom",
        )
        with patch(
            "app.services.patrimonios_service.patrimonios_repository.obter_por_patrimonio",
            return_value=equipamento(),
        ):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.criar_equipamento(FakeDb(), payload, self.admin)

        self.assertEqual(exc.exception.status_code, 400)
        self.assertIn("patrimônio", exc.exception.detail.lower())

    def test_criar_equipamento_persiste_evento_e_log(self):
        payload = EquipamentoCreate(
            numero_patrimonio="PAT-101",
            numero_serie="SER-101",
            tipo="notebook",
            marca="Dell",
            modelo="Latitude 5420",
            descricao="Uso corporativo",
            estado_conservacao="Novo",
        )
        db = FakeDb()
        objetos_salvos = []

        def salvar(_db, *objetos):
            objetos_salvos.extend(objetos)

        with (
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_por_patrimonio",
                return_value=None,
            ),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_por_serie",
                return_value=None,
            ),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.salvar",
                side_effect=salvar,
            ),
            patch("app.services.patrimonios_service.patrimonios_repository.commit") as commit_mock,
            patch("app.services.patrimonios_service.buscar_equipamento", side_effect=lambda _db, _id: objetos_salvos[0]),
            patch(
                "app.services.patrimonios_service.formatar_equipamento",
                side_effect=lambda item: {"id": item.id, "status": item.status},
            ),
        ):
            resultado = patrimonios_service.criar_equipamento(db, payload, self.admin)

        self.assertEqual(resultado, {"id": 101, "status": "disponivel"})
        self.assertEqual(objetos_salvos[0].numero_patrimonio, "PAT-101")
        self.assertEqual(objetos_salvos[1].tipo, "criacao")
        self.assertEqual(objetos_salvos[2].acao, "EQUIPAMENTO_CRIADO")
        commit_mock.assert_called_once_with(db)

    def test_criar_equipamento_traduz_conflito_de_integridade(self):
        payload = EquipamentoCreate(
            numero_patrimonio="PAT-101",
            tipo="monitor",
            marca="Dell",
            modelo="P2422H",
            estado_conservacao="Novo",
        )
        db = FakeDb()
        conflito = IntegrityError("insert", {}, Exception("unique"))
        with (
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_por_patrimonio",
                return_value=None,
            ),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_por_serie",
                return_value=None,
            ),
            patch("app.services.patrimonios_service.patrimonios_repository.salvar"),
            patch("app.services.patrimonios_service.patrimonios_repository.commit", side_effect=conflito),
        ):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.criar_equipamento(db, payload, self.admin)

        self.assertEqual(exc.exception.status_code, 409)
        self.assertTrue(db.rollback_called)

    def test_editar_equipamento_baixado_e_bloqueado(self):
        item = equipamento(status="baixado", ativo=False)
        with patch("app.services.patrimonios_service.buscar_equipamento", return_value=item):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.editar_equipamento(
                    FakeDb(), 10, EquipamentoUpdate(modelo="Outro"), self.admin
                )

        self.assertEqual(exc.exception.status_code, 400)

    def test_editar_nao_permite_trocar_tipo_de_equipamento_vinculado(self):
        item = equipamento(status="vinculado", tipo="monitor")
        with patch("app.services.patrimonios_service.buscar_equipamento", return_value=item):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.editar_equipamento(
                    FakeDb(), 10, EquipamentoUpdate(tipo="notebook"), self.admin
                )

        self.assertEqual(exc.exception.status_code, 400)

    def test_desvincular_bloqueia_item_com_autorizacao_entregue_em_aberto(self):
        item = equipamento(status="vinculado")
        vinculo = SimpleNamespace(id=1, user_id=2, observacoes=None)
        with (
            patch("app.services.patrimonios_service.buscar_equipamento", return_value=item),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=vinculo,
            ),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.existe_autorizacao_entregue_em_aberto",
                return_value=True,
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.desvincular_equipamento(
                    FakeDb(), 10, patrimonios_service.DesvinculoCreate(), self.admin
                )

        self.assertEqual(exc.exception.status_code, 409)

    def test_vincular_rejeita_equipamento_indisponivel(self):
        item = equipamento(status="manutencao")
        usuario = SimpleNamespace(id=2, ativo=True)
        with (
            patch("app.services.patrimonios_service.buscar_equipamento", return_value=item),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_usuario_bloqueado",
                return_value=usuario,
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.vincular_equipamento(
                    FakeDb(), 10, VinculoCreate(user_id=2), self.admin
                )

        self.assertEqual(exc.exception.status_code, 400)

    def test_vincular_segunda_maquina_principal_exige_confirmacao(self):
        item = equipamento(tipo="notebook")
        usuario = SimpleNamespace(id=2, ativo=True)
        with (
            patch("app.services.patrimonios_service.buscar_equipamento", return_value=item),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_usuario_bloqueado",
                return_value=usuario,
            ),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=None,
            ),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.contar_maquinas_principais_ativas",
                return_value=1,
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.vincular_equipamento(
                    FakeDb(), 10, VinculoCreate(user_id=2), self.admin
                )

        self.assertEqual(exc.exception.status_code, 400)
        self.assertIn("máquina principal", exc.exception.detail.lower())

    def test_vincular_traduz_concorrencia_e_faz_rollback(self):
        item = equipamento(tipo="monitor")
        usuario = SimpleNamespace(id=2, ativo=True)
        db = FakeDb()
        with (
            patch("app.services.patrimonios_service.buscar_equipamento", return_value=item),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_usuario_bloqueado",
                return_value=usuario,
            ),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=None,
            ),
            patch("app.services.patrimonios_service.patrimonios_repository.salvar"),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.commit",
                side_effect=IntegrityError("insert", {}, Exception("unique")),
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.vincular_equipamento(
                    db, 10, VinculoCreate(user_id=2), self.admin
                )

        self.assertEqual(exc.exception.status_code, 409)
        self.assertTrue(db.rollback_called)

    def test_iniciar_manutencao_altera_status_e_estado(self):
        item = equipamento(tipo="monitor")
        with (
            patch("app.services.patrimonios_service.buscar_equipamento", side_effect=[item, item]),
            patch(
                "app.services.patrimonios_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=None,
            ),
            patch("app.services.patrimonios_service.patrimonios_repository.salvar") as salvar_mock,
            patch("app.services.patrimonios_service.patrimonios_repository.commit") as commit_mock,
            patch(
                "app.services.patrimonios_service.formatar_equipamento",
                side_effect=lambda equipamento_: {"status": equipamento_.status},
            ),
        ):
            resultado = patrimonios_service.iniciar_manutencao(
                FakeDb(),
                10,
                ManutencaoCreate(observacoes="Troca de tela", estado_conservacao="Em reparo"),
                self.admin,
            )

        self.assertEqual(resultado["status"], "manutencao")
        self.assertEqual(item.estado_conservacao, "Em reparo")
        salvar_mock.assert_called_once()
        commit_mock.assert_called_once()

    def test_baixa_e_idempotente_quando_ja_baixado(self):
        item = equipamento(status="baixado", ativo=False)
        with (
            patch("app.services.patrimonios_service.buscar_equipamento", return_value=item),
            patch(
                "app.services.patrimonios_service.formatar_equipamento",
                return_value={"status": "baixado"},
            ),
            patch("app.services.patrimonios_service.patrimonios_repository.salvar") as salvar_mock,
        ):
            resultado = patrimonios_service.baixar_equipamento(
                FakeDb(), 10, BaixaCreate(motivo="Fim da vida util"), self.admin
            )

        self.assertEqual(resultado, {"status": "baixado"})
        salvar_mock.assert_not_called()

    def test_baixa_rejeita_equipamento_reservado(self):
        item = equipamento(status="reservado")
        with patch("app.services.patrimonios_service.buscar_equipamento", return_value=item):
            with self.assertRaises(HTTPException) as exc:
                patrimonios_service.baixar_equipamento(
                    FakeDb(), 10, BaixaCreate(motivo="Fim da vida util"), self.admin
                )

        self.assertEqual(exc.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
