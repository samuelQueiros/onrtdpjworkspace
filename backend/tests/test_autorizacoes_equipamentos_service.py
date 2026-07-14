import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.schemas.patrimonio import (
    AceiteSolicitacaoCreate,
    AprovacaoSolicitacaoCreate,
    DevolucaoSolicitacaoCreate,
    EntregaSolicitacaoCreate,
    RejeicaoSolicitacaoCreate,
    SolicitacaoEquipamentoCreate,
)
from app.services import autorizacoes_equipamentos_service as service


class FakeDb:
    def __init__(self):
        self.rollback_called = False

    def rollback(self):
        self.rollback_called = True


def equipamento(**alteracoes):
    dados = {
        "id": 10,
        "numero_patrimonio": "PAT-10",
        "numero_serie": "SER-10",
        "tipo": "monitor",
        "marca": "Dell",
        "modelo": "P2422H",
        "descricao": "Monitor corporativo",
        "estado_conservacao": "Bom",
        "status": "disponivel",
        "ativo": True,
    }
    dados.update(alteracoes)
    return SimpleNamespace(**dados)


def item_solicitacao(**alteracoes):
    dados = {
        "id": 101,
        "equipamento_id": 10,
        "status_item": "solicitado",
        "motivo_remocao": None,
        "reservado_em": None,
        "reserva_liberada_em": None,
        "vinculo_criado_entrega_id": None,
        "numero_patrimonio_snapshot": "PAT-10",
        "numero_serie_snapshot": "SER-10",
        "tipo_snapshot": "monitor",
        "marca_modelo_snapshot": "Dell P2422H",
        "estado_conservacao_snapshot": "Bom",
        "observacoes_snapshot": None,
        "entregue_em": None,
        "devolvido_em": None,
        "estado_conservacao_devolucao": None,
        "observacoes_devolucao": None,
    }
    dados.update(alteracoes)
    return SimpleNamespace(**dados)


def solicitacao(**alteracoes):
    dados = {
        "id": 50,
        "user_id": 2,
        "tipo_solicitacao": "item_diferente",
        "status": "pendente",
        "itens": [item_solicitacao()],
    }
    dados.update(alteracoes)
    return SimpleNamespace(**dados)


class AutorizacoesEquipamentosServiceTests(unittest.TestCase):
    def setUp(self):
        self.colaborador = SimpleNamespace(
            id=2,
            nome="Gabriel",
            role="user",
            cpf_criptografado="cpf-criptografado",
            cargo=SimpleNamespace(nome="Desenvolvedor"),
            departamento=SimpleNamespace(nome="Tecnologia"),
        )
        self.admin = SimpleNamespace(id=1, nome="Administrador", role="admin")

    def test_buscar_solicitacao_bloqueia_outro_colaborador(self):
        registro = solicitacao(user_id=7)
        with patch(
            "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_solicitacao",
            return_value=registro,
        ):
            with self.assertRaises(HTTPException) as exc:
                service.buscar_solicitacao(FakeDb(), 50, self.colaborador)

        self.assertEqual(exc.exception.status_code, 403)

    def test_buscar_solicitacao_permite_administrador(self):
        registro = solicitacao(user_id=7)
        with patch(
            "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_solicitacao",
            return_value=registro,
        ):
            resultado = service.buscar_solicitacao(FakeDb(), 50, self.admin)

        self.assertIs(resultado, registro)

    def test_aceite_so_pode_ser_registrado_pelo_titular_mesmo_se_usuario_for_admin(self):
        registro = solicitacao(user_id=2, status="aguardando_aceite")
        outro_admin = SimpleNamespace(id=9, nome="Outro administrador", role="admin")
        request = SimpleNamespace(client=None, state=SimpleNamespace(request_id="req-1"))
        with patch(
            "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
            return_value=registro,
        ):
            with self.assertRaises(HTTPException) as exc:
                service.registrar_aceite(
                    FakeDb(),
                    50,
                    AceiteSolicitacaoCreate(declaracao_aceite=True, local_aceite="Brasilia"),
                    outro_admin,
                    request,
                )

        self.assertEqual(exc.exception.status_code, 403)

    def test_admin_titular_recebe_acao_pessoal_de_aceite(self):
        registro = solicitacao(user_id=self.admin.id, status="aguardando_aceite")

        self.assertEqual(service._acoes_permitidas(registro, self.admin), ["aceitar"])

    def test_outro_admin_nao_recebe_acao_de_aceite(self):
        registro = solicitacao(user_id=2, status="aguardando_aceite")

        self.assertEqual(service._acoes_permitidas(registro, self.admin), [])

    def test_admin_titular_pode_analisar_ou_cancelar_solicitacao_pendente(self):
        registro = solicitacao(user_id=self.admin.id, status="pendente")

        self.assertEqual(
            service._acoes_permitidas(registro, self.admin),
            ["aprovar", "rejeitar", "cancelar"],
        )

    def test_colaborador_pode_cancelar_propria_solicitacao_pendente(self):
        registro = solicitacao(user_id=self.colaborador.id, status="pendente")

        self.assertEqual(service._acoes_permitidas(registro, self.colaborador), ["cancelar"])

    def test_criar_solicitacao_de_item_vinculado_salva_snapshots(self):
        db = FakeDb()
        item = equipamento(status="vinculado")
        objetos_salvos = []

        def salvar(_db, *objetos):
            objetos_salvos.extend(objetos)

        def flush(_db):
            registro = objetos_salvos[0]
            registro.id = 50
            for indice, item_registro in enumerate(registro.itens, start=101):
                item_registro.id = indice

        with (
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_equipamentos_por_ids",
                return_value=[item],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.listar_vinculos_ativos_usuario",
                return_value=[SimpleNamespace(equipamento_id=10)],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.existe_solicitacao_concorrente",
                return_value=False,
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.salvar",
                side_effect=salvar,
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.flush",
                side_effect=flush,
            ),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.commit") as commit_mock,
            patch(
                "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
                side_effect=lambda _db, _id, _user: objetos_salvos[0],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.formatar_solicitacao",
                side_effect=lambda registro, _user: {
                    "id": registro.id,
                    "status": registro.status,
                    "itens": len(registro.itens),
                },
            ),
        ):
            resultado = service.criar_solicitacao(
                db,
                SolicitacaoEquipamentoCreate(
                    tipo_solicitacao="itens_vinculados",
                    equipamento_ids=[10],
                    observacoes="Levar para trabalho remoto",
                ),
                self.colaborador,
            )

        registro = objetos_salvos[0]
        self.assertEqual(resultado, {"id": 50, "status": "pendente", "itens": 1})
        self.assertEqual(registro.nome_colaborador_snapshot, "Gabriel")
        self.assertEqual(registro.cargo_snapshot, "Desenvolvedor")
        self.assertEqual(registro.departamento_snapshot, "Tecnologia")
        self.assertEqual(registro.itens[0].numero_patrimonio_snapshot, "PAT-10")
        commit_mock.assert_called_once_with(db)

    def test_criar_solicitacao_rejeita_item_diferente_indisponivel(self):
        item = equipamento(status="reservado")
        with (
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_equipamentos_por_ids",
                return_value=[item],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.listar_vinculos_ativos_usuario",
                return_value=[],
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                service.criar_solicitacao(
                    FakeDb(),
                    SolicitacaoEquipamentoCreate(
                        tipo_solicitacao="item_diferente", equipamento_ids=[10]
                    ),
                    self.colaborador,
                )

        self.assertEqual(exc.exception.status_code, 409)

    def test_criar_solicitacao_rejeita_concorrencia_para_mesmo_item(self):
        item = equipamento()
        with (
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_equipamentos_por_ids",
                return_value=[item],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.listar_vinculos_ativos_usuario",
                return_value=[],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=None,
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.existe_solicitacao_concorrente",
                return_value=True,
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                service.criar_solicitacao(
                    FakeDb(),
                    SolicitacaoEquipamentoCreate(
                        tipo_solicitacao="item_diferente", equipamento_ids=[10]
                    ),
                    self.colaborador,
                )

        self.assertEqual(exc.exception.status_code, 409)
        self.assertIn("andamento", exc.exception.detail)

    def test_aprovacao_parcial_exige_motivo(self):
        registro = solicitacao(
            itens=[item_solicitacao(id=101), item_solicitacao(id=102, equipamento_id=11)]
        )
        with patch(
            "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
            return_value=registro,
        ):
            with self.assertRaises(HTTPException) as exc:
                service.aprovar_solicitacao(
                    FakeDb(),
                    50,
                    AprovacaoSolicitacaoCreate(item_ids_aprovados=[101]),
                    self.admin,
                )

        self.assertEqual(exc.exception.status_code, 400)
        self.assertIn("parcial", exc.exception.detail)

    def test_aprovar_item_diferente_reserva_equipamento(self):
        registro = solicitacao()
        item = equipamento()
        with (
            patch(
                "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
                return_value=registro,
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_equipamentos_por_ids",
                return_value=[item],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=None,
            ),
            patch("app.services.autorizacoes_equipamentos_service._evento", return_value=SimpleNamespace()),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.salvar"),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.commit") as commit_mock,
            patch(
                "app.services.autorizacoes_equipamentos_service.formatar_solicitacao",
                side_effect=lambda solicitacao_, _user: {"status": solicitacao_.status},
            ),
        ):
            resultado = service.aprovar_solicitacao(
                FakeDb(),
                50,
                AprovacaoSolicitacaoCreate(item_ids_aprovados=[101]),
                self.admin,
            )

        self.assertEqual(resultado, {"status": "aguardando_entrega"})
        self.assertEqual(item.status, "reservado")
        self.assertEqual(registro.itens[0].status_item, "aprovado")
        self.assertIsNotNone(registro.itens[0].reservado_em)
        commit_mock.assert_called_once()

    def test_aprovacao_traduz_conflito_concorrente_e_faz_rollback(self):
        registro = solicitacao()
        item = equipamento()
        db = FakeDb()
        with (
            patch(
                "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
                return_value=registro,
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_equipamentos_por_ids",
                return_value=[item],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=None,
            ),
            patch("app.services.autorizacoes_equipamentos_service._evento", return_value=SimpleNamespace()),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.salvar"),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.commit",
                side_effect=IntegrityError("update", {}, Exception("unique")),
            ),
        ):
            with self.assertRaises(HTTPException) as exc:
                service.aprovar_solicitacao(
                    db,
                    50,
                    AprovacaoSolicitacaoCreate(item_ids_aprovados=[101]),
                    self.admin,
                )

        self.assertEqual(exc.exception.status_code, 409)
        self.assertTrue(db.rollback_called)

    def test_rejeitar_solicitacao_registra_motivo(self):
        registro = solicitacao()
        with (
            patch(
                "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
                return_value=registro,
            ),
            patch("app.services.autorizacoes_equipamentos_service._evento", return_value=SimpleNamespace()),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.salvar"),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.commit"),
            patch(
                "app.services.autorizacoes_equipamentos_service.formatar_solicitacao",
                side_effect=lambda solicitacao_, _user: {"status": solicitacao_.status},
            ),
        ):
            resultado = service.rejeitar_solicitacao(
                FakeDb(),
                50,
                RejeicaoSolicitacaoCreate(motivo_rejeicao="Equipamento indisponivel"),
                self.admin,
            )

        self.assertEqual(resultado, {"status": "rejeitada"})
        self.assertEqual(registro.motivo_rejeicao, "Equipamento indisponivel")

    def test_entrega_de_item_ja_vinculado_avanca_para_aceite(self):
        registro = solicitacao(
            tipo_solicitacao="itens_vinculados",
            status="aguardando_entrega",
            itens=[item_solicitacao(status_item="aprovado")],
        )
        item = equipamento(status="vinculado")
        payload = EntregaSolicitacaoCreate(
            responsavel_entrega_nome="Administrador",
            responsavel_entrega_cargo="Gerente",
            local_entrega="Escritorio",
            itens=[{"item_id": 101, "estado_conservacao": "Bom", "observacoes": "Conferido"}],
        )
        versao = SimpleNamespace(id=3, codigo="v1")
        with (
            patch(
                "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
                return_value=registro,
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_equipamentos_por_ids",
                return_value=[item],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=SimpleNamespace(id=90, user_id=2),
            ),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.flush"),
            patch("app.services.autorizacoes_equipamentos_service._evento", return_value=SimpleNamespace()),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.salvar"),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.commit") as commit_mock,
            patch(
                "app.services.termos_equipamentos_service.garantir_versao_termo",
                return_value=versao,
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.formatar_solicitacao",
                side_effect=lambda solicitacao_, _user: {"status": solicitacao_.status},
            ),
        ):
            resultado = service.registrar_entrega(FakeDb(), 50, payload, self.admin)

        self.assertEqual(resultado, {"status": "aguardando_aceite"})
        self.assertEqual(registro.itens[0].status_item, "entregue")
        self.assertEqual(item.estado_conservacao, "Bom")
        self.assertIs(registro.termo_versao, versao)
        commit_mock.assert_called_once()

    def test_entrega_exige_estado_de_todos_os_itens_aprovados(self):
        registro = solicitacao(
            status="aguardando_entrega",
            itens=[
                item_solicitacao(id=101, status_item="aprovado"),
                item_solicitacao(id=102, equipamento_id=11, status_item="aprovado"),
            ],
        )
        payload = EntregaSolicitacaoCreate(
            responsavel_entrega_nome="Administrador",
            responsavel_entrega_cargo="Gerente",
            local_entrega="Escritorio",
            itens=[{"item_id": 101, "estado_conservacao": "Bom"}],
        )
        with patch(
            "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
            return_value=registro,
        ):
            with self.assertRaises(HTTPException) as exc:
                service.registrar_entrega(FakeDb(), 50, payload, self.admin)

        self.assertEqual(exc.exception.status_code, 400)

    def test_devolucao_desvincula_item_criado_na_entrega(self):
        registro = solicitacao(
            status="entregue",
            itens=[item_solicitacao(status_item="entregue", vinculo_criado_entrega_id=90)],
        )
        item = equipamento(status="vinculado")
        vinculo = SimpleNamespace(id=90, user_id=2, desvinculado_em=None, desvinculado_por_id=None)
        payload = DevolucaoSolicitacaoCreate(
            itens=[
                {
                    "item_id": 101,
                    "situacao": "devolvido",
                    "estado_conservacao": "Bom",
                    "observacoes": "Sem avarias",
                }
            ],
            estado_conservacao_geral="Bom",
            observacoes="Recebido e conferido",
        )
        with (
            patch(
                "app.services.autorizacoes_equipamentos_service.buscar_solicitacao",
                return_value=registro,
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_equipamentos_por_ids",
                return_value=[item],
            ),
            patch(
                "app.services.autorizacoes_equipamentos_service.patrimonios_repository.obter_vinculo_ativo",
                return_value=vinculo,
            ),
            patch("app.services.autorizacoes_equipamentos_service._evento", return_value=SimpleNamespace()),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.salvar"),
            patch("app.services.autorizacoes_equipamentos_service.patrimonios_repository.commit") as commit_mock,
            patch(
                "app.services.autorizacoes_equipamentos_service.formatar_solicitacao",
                side_effect=lambda solicitacao_, _user: {"status": solicitacao_.status},
            ),
        ):
            resultado = service.registrar_devolucao(FakeDb(), 50, payload, self.admin)

        self.assertEqual(resultado, {"status": "devolvida"})
        self.assertEqual(registro.itens[0].status_item, "devolvido")
        self.assertEqual(item.status, "disponivel")
        self.assertIsNotNone(vinculo.desvinculado_em)
        commit_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
