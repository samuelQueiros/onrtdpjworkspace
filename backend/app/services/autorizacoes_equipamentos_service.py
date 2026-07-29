import json
import math
from datetime import datetime

from fastapi import HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.cpf import mascarar_cpf
from app.core.crypto import descriptografar_dado_sensivel
from app.core.security import obter_ip_cliente
from app.models.log import Log
from app.models.patrimonio import (
    STATUS_SOLICITACAO,
    Equipamento,
    EquipamentoEvento,
    EquipamentoVinculo,
    SolicitacaoEquipamento,
    SolicitacaoEquipamentoEvento,
    SolicitacaoEquipamentoItem,
    agora_utc,
)
from app.models.user import User
from app.repositories import patrimonios_repository
from app.schemas.patrimonio import (
    AceiteSolicitacaoCreate,
    AprovacaoSolicitacaoCreate,
    CancelamentoSolicitacaoCreate,
    DevolucaoSolicitacaoCreate,
    EntregaSolicitacaoCreate,
    RejeicaoSolicitacaoCreate,
    SolicitacaoEquipamentoCreate,
)

MAQUINAS_PRINCIPAIS = {"notebook", "desktop"}


def _identificacao(equipamento: Equipamento) -> str:
    return equipamento.numero_patrimonio or equipamento.numero_serie or f"#{equipamento.id}"


def _evento(
    solicitacao: SolicitacaoEquipamento,
    tipo: str,
    usuario_id: int,
    status_anterior: str | None = None,
    status_novo: str | None = None,
    detalhes: dict | str | None = None,
) -> SolicitacaoEquipamentoEvento:
    return SolicitacaoEquipamentoEvento(
        solicitacao=solicitacao,
        tipo=tipo,
        status_anterior=status_anterior,
        status_novo=status_novo,
        detalhes=(json.dumps(detalhes, ensure_ascii=False, sort_keys=True) if isinstance(detalhes, dict) else detalhes),
        criado_por_id=usuario_id,
    )


def _log(usuario_id: int, acao: str, solicitacao_id: int | None, detalhe: str = "") -> Log:
    identificador = f"Solicitacao de equipamento #{solicitacao_id}" if solicitacao_id else "Solicitacao de equipamento"
    return Log(user_id=usuario_id, acao=acao, detalhes=f"{identificador}{': ' + detalhe if detalhe else ''}")


def _snapshot_item(equipamento: Equipamento, observacoes: str | None = None) -> dict:
    return {
        "numero_patrimonio_snapshot": equipamento.numero_patrimonio,
        "numero_serie_snapshot": equipamento.numero_serie,
        "tipo_snapshot": equipamento.tipo,
        "marca_modelo_snapshot": f"{equipamento.marca} {equipamento.modelo}".strip(),
        "estado_conservacao_snapshot": equipamento.estado_conservacao,
        "observacoes_snapshot": observacoes or equipamento.descricao,
    }


def _atualizar_snapshot_item(
    item: SolicitacaoEquipamentoItem,
    equipamento: Equipamento,
    observacoes: str | None = None,
) -> None:
    for campo, valor in _snapshot_item(equipamento, observacoes).items():
        setattr(item, campo, valor)


def _formatar_item(item: SolicitacaoEquipamentoItem) -> dict:
    return {
        "id": item.id,
        "equipamento_id": item.equipamento_id,
        "status_item": item.status_item,
        "motivo_remocao": item.motivo_remocao,
        "numero_patrimonio_snapshot": item.numero_patrimonio_snapshot,
        "numero_serie_snapshot": item.numero_serie_snapshot,
        "tipo_snapshot": item.tipo_snapshot,
        "marca_modelo_snapshot": item.marca_modelo_snapshot,
        "estado_conservacao_snapshot": item.estado_conservacao_snapshot,
        "observacoes_snapshot": item.observacoes_snapshot,
        "entregue_em": item.entregue_em,
        "devolvido_em": item.devolvido_em,
        "estado_conservacao_devolucao": item.estado_conservacao_devolucao,
        "observacoes_devolucao": item.observacoes_devolucao,
    }


def _acoes_permitidas(solicitacao: SolicitacaoEquipamento, current_user: User) -> list[str]:
    # O aceite e sempre pessoal, inclusive quando o titular possui perfil
    # administrativo. As demais etapas continuam seguindo o perfil do usuario.
    if solicitacao.user_id == current_user.id and solicitacao.status == "aguardando_aceite":
        return ["aceitar"]
    if current_user.role == "admin":
        if solicitacao.status == "pendente":
            acoes = ["aprovar", "rejeitar"]
            if solicitacao.user_id == current_user.id:
                acoes.append("cancelar")
            return acoes
        if solicitacao.status == "aguardando_entrega":
            return ["registrar_entrega", "cancelar"]
        if solicitacao.status in {"aceite_registrado_aguardando_documento", "entregue"}:
            acoes = ["regenerar_documento"]
            if solicitacao.status == "entregue":
                acoes.append("registrar_devolucao")
            return acoes
        return []
    if solicitacao.user_id == current_user.id and solicitacao.status == "pendente":
        return ["cancelar"]
    return []


def formatar_solicitacao(solicitacao: SolicitacaoEquipamento, current_user: User) -> dict:
    cpf = descriptografar_dado_sensivel(solicitacao.cpf_snapshot_criptografado)
    return {
        "id": solicitacao.id,
        "user_id": solicitacao.user_id,
        "user_nome": solicitacao.nome_colaborador_snapshot,
        "user_cpf_mascarado": mascarar_cpf(cpf),
        "tipo_solicitacao": solicitacao.tipo_solicitacao,
        "status": solicitacao.status,
        "observacoes": solicitacao.observacoes,
        "criado_em": solicitacao.criado_em,
        "atualizado_em": solicitacao.atualizado_em,
        "aprovado_em": solicitacao.aprovado_em,
        "aprovado_por_nome": solicitacao.aprovado_por.nome if solicitacao.aprovado_por else None,
        "rejeitado_em": solicitacao.rejeitado_em,
        "rejeitado_por_nome": solicitacao.rejeitado_por.nome if solicitacao.rejeitado_por else None,
        "motivo_rejeicao": solicitacao.motivo_rejeicao,
        "cancelado_em": solicitacao.cancelado_em,
        "motivo_cancelamento": solicitacao.motivo_cancelamento,
        "entregue_em": solicitacao.entregue_em,
        "entregue_por_nome": solicitacao.entregue_por.nome if solicitacao.entregue_por else None,
        "responsavel_entrega_nome": solicitacao.responsavel_entrega_nome,
        "responsavel_entrega_cargo": solicitacao.responsavel_entrega_cargo,
        "local_entrega": solicitacao.local_entrega,
        "aceito_em": solicitacao.aceito_em,
        "local_aceite": solicitacao.local_aceite,
        "termo_versao": solicitacao.termo_versao.codigo if solicitacao.termo_versao else None,
        "termo_conteudo_hash": solicitacao.termo_versao.conteudo_hash if solicitacao.termo_versao else None,
        "termo_clausulas": solicitacao.termo_versao.clausulas if solicitacao.termo_versao else None,
        "documento_id": solicitacao.documento_id,
        "documento_hash": solicitacao.documento_hash,
        "documento_status": solicitacao.documento_status,
        "documento_erro": solicitacao.documento_erro if current_user.role == "admin" else None,
        "devolvido_em": solicitacao.devolvido_em,
        "estado_conservacao_devolucao": solicitacao.estado_conservacao_devolucao,
        "itens_ausentes_devolucao": solicitacao.itens_ausentes_devolucao,
        "observacoes_devolucao": solicitacao.observacoes_devolucao,
        "itens": [_formatar_item(item) for item in solicitacao.itens],
        "eventos": [
            {
                "id": evento.id,
                "tipo": evento.tipo,
                "status_anterior": evento.status_anterior,
                "status_novo": evento.status_novo,
                "detalhes": evento.detalhes,
                "criado_por_nome": evento.criado_por.nome if evento.criado_por else "Sistema",
                "criado_em": evento.criado_em,
            }
            for evento in solicitacao.eventos
        ],
        "acoes_permitidas": _acoes_permitidas(solicitacao, current_user),
    }


def buscar_solicitacao(
    db: Session,
    solicitacao_id: int,
    current_user: User,
    bloquear: bool = False,
) -> SolicitacaoEquipamento:
    solicitacao = patrimonios_repository.obter_solicitacao(db, solicitacao_id, bloquear)
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitacao de equipamento nao encontrada")
    if current_user.role != "admin" and solicitacao.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return solicitacao


def _validar_dados_termo(user: User) -> tuple[str, str, str, str]:
    if not user.cpf_criptografado:
        raise HTTPException(status_code=400, detail="Cadastre o CPF do colaborador antes de solicitar equipamentos")
    if not user.cargo:
        raise HTTPException(status_code=400, detail="Cadastre o cargo do colaborador antes da solicitacao")
    if not user.departamento:
        raise HTTPException(status_code=400, detail="Cadastre o departamento do colaborador antes da solicitacao")
    return user.nome, user.cpf_criptografado, user.cargo.nome, user.departamento.nome


def criar_solicitacao(
    db: Session,
    payload: SolicitacaoEquipamentoCreate,
    current_user: User,
) -> dict:
    nome, cpf_criptografado, cargo, departamento = _validar_dados_termo(current_user)
    ids = sorted(payload.equipamento_ids)
    equipamentos = patrimonios_repository.obter_equipamentos_por_ids(db, ids, bloquear=True)
    if len(equipamentos) != len(ids):
        raise HTTPException(status_code=404, detail="Um ou mais equipamentos nao foram encontrados")

    vinculos = {
        vinculo.equipamento_id: vinculo
        for vinculo in patrimonios_repository.listar_vinculos_ativos_usuario(db, current_user.id)
    }
    for equipamento in equipamentos:
        if payload.tipo_solicitacao == "itens_vinculados":
            if equipamento.id not in vinculos or not equipamento.ativo or equipamento.status != "vinculado":
                raise HTTPException(status_code=400, detail=f"Equipamento {_identificacao(equipamento)} nao esta vinculado a voce")
        else:
            if not equipamento.ativo or equipamento.status != "disponivel":
                raise HTTPException(status_code=409, detail=f"Equipamento {_identificacao(equipamento)} nao esta disponivel")
            if patrimonios_repository.obter_vinculo_ativo(db, equipamento.id):
                raise HTTPException(status_code=409, detail=f"Equipamento {_identificacao(equipamento)} possui vinculo ativo")
        if patrimonios_repository.existe_solicitacao_concorrente(db, current_user.id, equipamento.id):
            raise HTTPException(status_code=409, detail=f"Ja existe solicitacao em andamento para {_identificacao(equipamento)}")

    solicitacao = SolicitacaoEquipamento(
        user_id=current_user.id,
        tipo_solicitacao=payload.tipo_solicitacao,
        status="pendente",
        observacoes=payload.observacoes,
        nome_colaborador_snapshot=nome,
        cpf_snapshot_criptografado=cpf_criptografado,
        cargo_snapshot=cargo,
        departamento_snapshot=departamento,
    )
    for equipamento in equipamentos:
        solicitacao.itens.append(
            SolicitacaoEquipamentoItem(
                equipamento_id=equipamento.id,
                status_item="solicitado",
                **_snapshot_item(equipamento),
            )
        )
    _evento(solicitacao, "criacao", current_user.id, None, "pendente", {"equipamentos": ids})
    patrimonios_repository.salvar(db, solicitacao)
    patrimonios_repository.flush(db)
    patrimonios_repository.salvar(db, _log(current_user.id, "AUTORIZACAO_EQUIPAMENTO_CRIADA", solicitacao.id))
    try:
        patrimonios_repository.commit(db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Solicitacao concorrente detectada. Atualize os equipamentos.") from exc
    return formatar_solicitacao(buscar_solicitacao(db, solicitacao.id, current_user), current_user)


def listar_minhas_solicitacoes(db: Session, current_user: User) -> list[dict]:
    return [formatar_solicitacao(item, current_user) for item in patrimonios_repository.listar_solicitacoes_usuario(
        db, current_user.id
    )]


def listar_solicitacoes_admin(
    db: Session,
    current_user: User,
    status: str | None = None,
    user_id: int | None = None,
    equipamento_id: int | None = None,
    criado_de: datetime | None = None,
    criado_ate: datetime | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    if status and status not in STATUS_SOLICITACAO:
        raise HTTPException(status_code=400, detail="Status de solicitacao invalido")
    if criado_de and criado_ate and criado_de > criado_ate:
        raise HTTPException(status_code=400, detail="A data inicial nao pode ser posterior a data final")
    items, total = patrimonios_repository.listar_solicitacoes_admin(
        db,
        status,
        user_id,
        equipamento_id,
        criado_de,
        criado_ate,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return {
        "items": [
        formatar_solicitacao(item, current_user)
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total else 0,
    }


def cancelar_solicitacao(
    db: Session,
    solicitacao_id: int,
    payload: CancelamentoSolicitacaoCreate,
    current_user: User,
) -> dict:
    solicitacao = buscar_solicitacao(db, solicitacao_id, current_user, bloquear=True)
    if solicitacao.status == "cancelada":
        return formatar_solicitacao(solicitacao, current_user)
    status_permitidos = {"pendente", "aguardando_entrega"} if current_user.role == "admin" else {"pendente"}
    if solicitacao.status not in status_permitidos:
        raise HTTPException(status_code=400, detail="Solicitacao nao pode ser cancelada neste estado")
    if current_user.role == "admin" and solicitacao.status == "aguardando_entrega" and not payload.motivo:
        raise HTTPException(status_code=400, detail="Informe o motivo do cancelamento administrativo")
    agora = agora_utc()
    if solicitacao.status == "aguardando_entrega":
        equipamentos = patrimonios_repository.obter_equipamentos_por_ids(
            db,
            sorted(item.equipamento_id for item in solicitacao.itens if item.status_item == "aprovado"),
            bloquear=True,
        )
        por_id = {equipamento.id: equipamento for equipamento in equipamentos}
        for item in solicitacao.itens:
            if item.reservado_em and not item.reserva_liberada_em:
                item.reserva_liberada_em = agora
                equipamento = por_id.get(item.equipamento_id)
                if equipamento and equipamento.status == "reservado":
                    equipamento.status = "disponivel"
    anterior = solicitacao.status
    solicitacao.status = "cancelada"
    solicitacao.cancelado_em = agora
    solicitacao.cancelado_por_id = current_user.id
    solicitacao.motivo_cancelamento = payload.motivo
    patrimonios_repository.salvar(
        db,
        _evento(solicitacao, "cancelamento", current_user.id, anterior, "cancelada", payload.motivo),
        _log(current_user.id, "AUTORIZACAO_EQUIPAMENTO_CANCELADA", solicitacao.id),
    )
    patrimonios_repository.commit(db)
    return formatar_solicitacao(buscar_solicitacao(db, solicitacao.id, current_user), current_user)


def _validar_maquinas_aprovadas(
    db: Session,
    solicitacao: SolicitacaoEquipamento,
    equipamentos: list[Equipamento],
    payload: AprovacaoSolicitacaoCreate,
) -> None:
    novas_maquinas = [item for item in equipamentos if item.tipo in MAQUINAS_PRINCIPAIS]
    if not novas_maquinas or solicitacao.tipo_solicitacao == "itens_vinculados":
        return
    if not patrimonios_repository.obter_usuario_bloqueado(db, solicitacao.user_id):
        raise HTTPException(status_code=404, detail="Colaborador da solicitacao nao encontrado")
    existentes = patrimonios_repository.contar_maquinas_principais_ativas(db, solicitacao.user_id)
    if existentes + len(novas_maquinas) > 1 and not payload.permitir_segunda_maquina:
        raise HTTPException(
            status_code=400,
            detail="A aprovacao criaria mais de uma maquina principal. Confirme e justifique a excecao.",
        )


def aprovar_solicitacao(
    db: Session,
    solicitacao_id: int,
    payload: AprovacaoSolicitacaoCreate,
    current_user: User,
) -> dict:
    solicitacao = buscar_solicitacao(db, solicitacao_id, current_user, bloquear=True)
    if solicitacao.status != "pendente":
        raise HTTPException(status_code=400, detail="Solicitacao nao esta pendente")
    itens_por_id = {item.id: item for item in solicitacao.itens}
    aprovados_ids = set(payload.item_ids_aprovados)
    if not aprovados_ids.issubset(itens_por_id):
        raise HTTPException(status_code=400, detail="Item informado nao pertence a solicitacao")
    removidos = [item for item in solicitacao.itens if item.id not in aprovados_ids]
    if removidos and not payload.motivo_ajuste:
        raise HTTPException(status_code=400, detail="Informe o motivo da aprovacao parcial")

    aprovados = [itens_por_id[item_id] for item_id in sorted(aprovados_ids)]
    equipamentos = patrimonios_repository.obter_equipamentos_por_ids(
        db, sorted(item.equipamento_id for item in aprovados), bloquear=True
    )
    equipamentos_por_id = {item.id: item for item in equipamentos}
    if len(equipamentos) != len(aprovados):
        raise HTTPException(status_code=409, detail="Um equipamento aprovado deixou de existir")

    _validar_maquinas_aprovadas(db, solicitacao, equipamentos, payload)
    agora = agora_utc()
    for item in aprovados:
        equipamento = equipamentos_por_id[item.equipamento_id]
        if not equipamento.ativo or equipamento.status in {"manutencao", "baixado", "reservado"}:
            raise HTTPException(status_code=409, detail=f"Equipamento {_identificacao(equipamento)} nao esta disponivel")
        vinculo = patrimonios_repository.obter_vinculo_ativo(db, equipamento.id, bloquear=True)
        if solicitacao.tipo_solicitacao == "itens_vinculados":
            if not vinculo or vinculo.user_id != solicitacao.user_id or equipamento.status != "vinculado":
                raise HTTPException(status_code=409, detail=f"Vinculo de {_identificacao(equipamento)} foi alterado")
        else:
            if vinculo or equipamento.status != "disponivel":
                raise HTTPException(status_code=409, detail=f"Equipamento {_identificacao(equipamento)} deixou de estar disponivel")
            equipamento.status = "reservado"
            item.reservado_em = agora
        _atualizar_snapshot_item(item, equipamento, item.observacoes_snapshot)
        item.status_item = "aprovado"

    for item in removidos:
        item.status_item = "removido"
        item.motivo_remocao = payload.motivo_ajuste
        item.removido_em = agora
        item.removido_por_id = current_user.id

    anterior = solicitacao.status
    solicitacao.status = "aguardando_entrega"
    solicitacao.aprovado_em = agora
    solicitacao.aprovado_por_id = current_user.id
    detalhes = {
        "itens_aprovados": sorted(aprovados_ids),
        "itens_removidos": sorted(item.id for item in removidos),
        "motivo_ajuste": payload.motivo_ajuste,
        "excecao_segunda_maquina": payload.permitir_segunda_maquina,
        "justificativa_excecao": payload.justificativa_excecao,
    }
    acao = "AUTORIZACAO_EQUIPAMENTO_APROVADA_PARCIAL" if removidos else "AUTORIZACAO_EQUIPAMENTO_APROVADA"
    patrimonios_repository.salvar(
        db,
        _evento(solicitacao, "aprovacao", current_user.id, anterior, solicitacao.status, detalhes),
        _log(current_user.id, acao, solicitacao.id, f"{len(aprovados)} item(ns) aprovado(s)"),
    )
    try:
        patrimonios_repository.commit(db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Outro administrador reservou um dos equipamentos") from exc
    return formatar_solicitacao(buscar_solicitacao(db, solicitacao.id, current_user), current_user)


def rejeitar_solicitacao(
    db: Session,
    solicitacao_id: int,
    payload: RejeicaoSolicitacaoCreate,
    current_user: User,
) -> dict:
    solicitacao = buscar_solicitacao(db, solicitacao_id, current_user, bloquear=True)
    if solicitacao.status != "pendente":
        raise HTTPException(status_code=400, detail="Somente solicitacao pendente pode ser rejeitada")
    anterior = solicitacao.status
    solicitacao.status = "rejeitada"
    solicitacao.rejeitado_em = agora_utc()
    solicitacao.rejeitado_por_id = current_user.id
    solicitacao.motivo_rejeicao = payload.motivo_rejeicao
    patrimonios_repository.salvar(
        db,
        _evento(solicitacao, "rejeicao", current_user.id, anterior, "rejeitada", payload.motivo_rejeicao),
        _log(current_user.id, "AUTORIZACAO_EQUIPAMENTO_REJEITADA", solicitacao.id),
    )
    patrimonios_repository.commit(db)
    return formatar_solicitacao(buscar_solicitacao(db, solicitacao.id, current_user), current_user)


def registrar_entrega(
    db: Session,
    solicitacao_id: int,
    payload: EntregaSolicitacaoCreate,
    current_user: User,
) -> dict:
    solicitacao = buscar_solicitacao(db, solicitacao_id, current_user, bloquear=True)
    if solicitacao.status != "aguardando_entrega":
        raise HTTPException(status_code=400, detail="Solicitacao nao esta aguardando entrega")
    aprovados = [item for item in solicitacao.itens if item.status_item == "aprovado"]
    payload_por_id = {item.item_id: item for item in payload.itens}
    if set(payload_por_id) != {item.id for item in aprovados}:
        raise HTTPException(status_code=400, detail="Informe o estado de todos os itens aprovados")
    equipamentos = patrimonios_repository.obter_equipamentos_por_ids(
        db, sorted(item.equipamento_id for item in aprovados), bloquear=True
    )
    equipamentos_por_id = {item.id: item for item in equipamentos}
    agora = agora_utc()
    novos_vinculos: list[tuple[SolicitacaoEquipamentoItem, EquipamentoVinculo]] = []

    if solicitacao.tipo_solicitacao == "item_diferente":
        if not patrimonios_repository.obter_usuario_bloqueado(db, solicitacao.user_id):
            raise HTTPException(status_code=404, detail="Colaborador da solicitacao nao encontrado")

    for item in aprovados:
        equipamento = equipamentos_por_id.get(item.equipamento_id)
        if not equipamento or not equipamento.ativo:
            raise HTTPException(status_code=409, detail="Equipamento aprovado nao esta mais ativo")
        vinculo = patrimonios_repository.obter_vinculo_ativo(db, equipamento.id, bloquear=True)
        if solicitacao.tipo_solicitacao == "itens_vinculados":
            if not vinculo or vinculo.user_id != solicitacao.user_id:
                raise HTTPException(status_code=409, detail=f"Vinculo de {_identificacao(equipamento)} foi alterado")
        else:
            if vinculo or equipamento.status != "reservado" or not item.reservado_em or item.reserva_liberada_em:
                raise HTTPException(status_code=409, detail=f"Reserva de {_identificacao(equipamento)} nao esta valida")
            maquina = equipamento.tipo in MAQUINAS_PRINCIPAIS
            existentes = patrimonios_repository.contar_maquinas_principais_ativas(db, solicitacao.user_id)
            if maquina and existentes + len([v for _, v in novos_vinculos if v.maquina_principal]) >= 1:
                if not payload.permitir_segunda_maquina:
                    raise HTTPException(status_code=400, detail="Entrega criaria segunda maquina principal sem excecao")
                if not payload.justificativa_excecao:
                    raise HTTPException(status_code=400, detail="Justifique a excecao de segunda maquina")
            vinculo = EquipamentoVinculo(
                equipamento_id=equipamento.id,
                user_id=solicitacao.user_id,
                vinculado_por_id=current_user.id,
                observacoes=f"Criado na entrega da solicitacao #{solicitacao.id}",
                maquina_principal=maquina,
                excecao_maquina_principal=maquina and payload.permitir_segunda_maquina,
                justificativa_excecao=payload.justificativa_excecao,
            )
            patrimonios_repository.salvar(db, vinculo)
            novos_vinculos.append((item, vinculo))
            equipamento.status = "vinculado"
            item.reserva_liberada_em = agora

        dados_entrega = payload_por_id[item.id]
        item.status_item = "entregue"
        item.entregue_em = agora
        _atualizar_snapshot_item(
            item,
            equipamento,
            dados_entrega.observacoes or item.observacoes_snapshot,
        )
        item.estado_conservacao_snapshot = dados_entrega.estado_conservacao
        equipamento.estado_conservacao = dados_entrega.estado_conservacao

    patrimonios_repository.flush(db)
    for item, vinculo in novos_vinculos:
        item.vinculo_criado_entrega_id = vinculo.id

    anterior = solicitacao.status
    solicitacao.status = "aguardando_aceite"
    solicitacao.entregue_em = agora
    solicitacao.entregue_por_id = current_user.id
    solicitacao.responsavel_entrega_nome = payload.responsavel_entrega_nome
    solicitacao.responsavel_entrega_cargo = payload.responsavel_entrega_cargo
    solicitacao.local_entrega = payload.local_entrega
    from app.services import termos_equipamentos_service

    solicitacao.termo_versao = termos_equipamentos_service.garantir_versao_termo(db)
    patrimonios_repository.salvar(
        db,
        _evento(
            solicitacao,
            "entrega",
            current_user.id,
            anterior,
            solicitacao.status,
            {
                "itens": sorted(item.id for item in aprovados),
                "local": payload.local_entrega,
                "excecao_segunda_maquina": payload.permitir_segunda_maquina,
                "justificativa_excecao": payload.justificativa_excecao,
            },
        ),
        _log(current_user.id, "AUTORIZACAO_EQUIPAMENTO_ENTREGA_REGISTRADA", solicitacao.id),
    )
    try:
        patrimonios_repository.commit(db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflito ao criar vinculo durante a entrega") from exc
    return formatar_solicitacao(buscar_solicitacao(db, solicitacao.id, current_user), current_user)


def registrar_aceite(
    db: Session,
    solicitacao_id: int,
    payload: AceiteSolicitacaoCreate,
    current_user: User,
    request: Request,
) -> dict:
    solicitacao = buscar_solicitacao(db, solicitacao_id, current_user, bloquear=True)
    if solicitacao.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="O aceite deve ser registrado pelo colaborador responsavel pela solicitacao",
        )
    if solicitacao.status == "entregue" and solicitacao.documento_id:
        return formatar_solicitacao(solicitacao, current_user)
    if solicitacao.status != "aguardando_aceite":
        raise HTTPException(status_code=400, detail="Solicitacao nao esta aguardando aceite")
    if any(item.status_item != "entregue" for item in solicitacao.itens if item.status_item != "removido"):
        raise HTTPException(status_code=409, detail="Nem todos os itens aprovados foram entregues")

    agora = agora_utc()
    anterior = solicitacao.status
    solicitacao.aceito_em = agora
    solicitacao.aceite_ip = obter_ip_cliente(request)
    solicitacao.aceite_request_id = getattr(request.state, "request_id", None)
    solicitacao.aceite_declaracao = True
    solicitacao.local_aceite = payload.local_aceite
    solicitacao.status = "aceite_registrado_aguardando_documento"
    solicitacao.documento_status = "pendente"
    patrimonios_repository.salvar(
        db,
        _evento(solicitacao, "aceite", current_user.id, anterior, solicitacao.status, {"local": payload.local_aceite}),
        _log(current_user.id, "AUTORIZACAO_EQUIPAMENTO_ACEITE_REGISTRADO", solicitacao.id),
    )
    patrimonios_repository.commit(db)

    try:
        from app.services import termos_equipamentos_service

        termos_equipamentos_service.gerar_termo_definitivo(db, solicitacao.id, current_user, regenerar=False)
    except Exception:
        db.rollback()
        # A geracao e recuperavel e o servico de termos registra a falha de forma
        # sanitizada. O aceite permanece preservado para uma regeneracao posterior.
    return formatar_solicitacao(buscar_solicitacao(db, solicitacao.id, current_user), current_user)


def regenerar_documento(db: Session, solicitacao_id: int, current_user: User) -> dict:
    solicitacao = buscar_solicitacao(db, solicitacao_id, current_user)
    if not solicitacao.aceito_em:
        raise HTTPException(status_code=400, detail="O termo so pode ser gerado apos o aceite")
    from app.services import termos_equipamentos_service

    try:
        termos_equipamentos_service.gerar_termo_definitivo(
            db, solicitacao.id, current_user, regenerar=True
        )
    except termos_equipamentos_service.TermoEquipamentoError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return formatar_solicitacao(buscar_solicitacao(db, solicitacao.id, current_user), current_user)


def registrar_devolucao(
    db: Session,
    solicitacao_id: int,
    payload: DevolucaoSolicitacaoCreate,
    current_user: User,
) -> dict:
    solicitacao = buscar_solicitacao(db, solicitacao_id, current_user, bloquear=True)
    if solicitacao.status == "devolvida":
        return formatar_solicitacao(solicitacao, current_user)
    if solicitacao.status != "entregue":
        raise HTTPException(status_code=400, detail="Somente solicitacao entregue pode ser devolvida")
    entregues = [item for item in solicitacao.itens if item.status_item == "entregue"]
    payload_por_id = {item.item_id: item for item in payload.itens}
    if set(payload_por_id) != {item.id for item in entregues}:
        raise HTTPException(status_code=400, detail="Registre a situacao de todos os itens entregues")
    equipamentos = patrimonios_repository.obter_equipamentos_por_ids(
        db, sorted(item.equipamento_id for item in entregues), bloquear=True
    )
    equipamentos_por_id = {item.id: item for item in equipamentos}
    agora = agora_utc()
    ausentes = []
    for item in entregues:
        dado = payload_por_id[item.id]
        equipamento = equipamentos_por_id[item.equipamento_id]
        status_anterior_equipamento = equipamento.status
        item.observacoes_devolucao = dado.observacoes
        if dado.situacao == "ausente":
            item.status_item = "ausente"
            ausentes.append(_identificacao(equipamento))
            patrimonios_repository.salvar(
                db,
                EquipamentoEvento(
                    equipamento_id=equipamento.id,
                    tipo="devolucao_ausente",
                    status_anterior=status_anterior_equipamento,
                    status_novo=equipamento.status,
                    estado_conservacao=equipamento.estado_conservacao,
                    observacoes=(
                        dado.observacoes
                        or f"Item ausente na devolucao da solicitacao #{solicitacao.id}"
                    ),
                    criado_por_id=current_user.id,
                ),
            )
            continue
        item.status_item = "devolvido"
        item.devolvido_em = agora
        item.estado_conservacao_devolucao = dado.estado_conservacao
        equipamento.estado_conservacao = dado.estado_conservacao
        if item.vinculo_criado_entrega_id:
            vinculo = patrimonios_repository.obter_vinculo_ativo(db, equipamento.id, bloquear=True)
            if vinculo and vinculo.id == item.vinculo_criado_entrega_id:
                vinculo.desvinculado_em = agora
                vinculo.desvinculado_por_id = current_user.id
                equipamento.status = "disponivel"
        evento_equipamento = EquipamentoEvento(
            equipamento_id=equipamento.id,
            tipo="devolucao",
            status_anterior=status_anterior_equipamento,
            status_novo=equipamento.status,
            estado_conservacao=dado.estado_conservacao,
            observacoes=f"Devolucao da solicitacao #{solicitacao.id}",
            criado_por_id=current_user.id,
        )
        patrimonios_repository.salvar(db, evento_equipamento)

    anterior = solicitacao.status
    solicitacao.status = "devolvida"
    solicitacao.devolvido_em = agora
    solicitacao.devolvido_por_id = solicitacao.user_id
    solicitacao.recebido_devolucao_por_id = current_user.id
    solicitacao.estado_conservacao_devolucao = payload.estado_conservacao_geral
    solicitacao.itens_ausentes_devolucao = ", ".join(ausentes) if ausentes else None
    solicitacao.observacoes_devolucao = payload.observacoes
    patrimonios_repository.salvar(
        db,
        _evento(
            solicitacao,
            "devolucao",
            current_user.id,
            anterior,
            "devolvida",
            {"ausentes": ausentes, "itens": sorted(payload_por_id)},
        ),
        _log(current_user.id, "AUTORIZACAO_EQUIPAMENTO_DEVOLUCAO_REGISTRADA", solicitacao.id),
    )
    patrimonios_repository.commit(db)
    return formatar_solicitacao(buscar_solicitacao(db, solicitacao.id, current_user), current_user)


def contar_pendentes(db: Session) -> int:
    return patrimonios_repository.contar_solicitacoes_pendentes(db)
