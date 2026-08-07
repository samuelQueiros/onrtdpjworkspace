import math

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.patrimonio import (
    STATUS_EQUIPAMENTO,
    TIPOS_EQUIPAMENTO,
    Equipamento,
    EquipamentoEvento,
    EquipamentoVinculo,
    agora_utc,
)
from app.models.user import User
from app.repositories import patrimonios_repository
from app.schemas.patrimonio import (
    BaixaCreate,
    DesvinculoCreate,
    EquipamentoCreate,
    EquipamentoUpdate,
    ManutencaoCreate,
    VinculoCreate,
)
from app.services import log_service

MAQUINAS_PRINCIPAIS = {"notebook", "desktop"}


def _texto_identificacao(equipamento: Equipamento) -> str:
    return equipamento.numero_patrimonio or equipamento.numero_serie or f"#{equipamento.id}"


def _vinculo_ativo(equipamento: Equipamento) -> EquipamentoVinculo | None:
    return next((vinculo for vinculo in equipamento.vinculos if vinculo.desvinculado_em is None), None)


def formatar_vinculo(vinculo: EquipamentoVinculo) -> dict:
    return {
        "id": vinculo.id,
        "equipamento_id": vinculo.equipamento_id,
        "user_id": vinculo.user_id,
        "user_nome": vinculo.usuario.nome if vinculo.usuario else "Colaborador",
        "vinculado_em": vinculo.vinculado_em,
        "desvinculado_em": vinculo.desvinculado_em,
        "vinculado_por_nome": vinculo.vinculado_por.nome if vinculo.vinculado_por else "Sistema",
        "desvinculado_por_nome": vinculo.desvinculado_por.nome if vinculo.desvinculado_por else None,
        "observacoes": vinculo.observacoes,
        "maquina_principal": vinculo.maquina_principal,
        "excecao_maquina_principal": vinculo.excecao_maquina_principal,
        "justificativa_excecao": vinculo.justificativa_excecao,
    }


def _acoes_permitidas(equipamento: Equipamento, vinculo: EquipamentoVinculo | None) -> list[str]:
    acoes = ["visualizar"]
    if equipamento.status != "baixado":
        acoes.append("editar")
    if equipamento.ativo and equipamento.status == "disponivel" and not vinculo:
        acoes.extend(["vincular", "iniciar_manutencao", "baixar"])
    if vinculo:
        acoes.append("desvincular")
    if equipamento.status == "manutencao":
        acoes.extend(["finalizar_manutencao", "baixar"])
    return acoes


def formatar_equipamento(equipamento: Equipamento) -> dict:
    vinculo = _vinculo_ativo(equipamento)
    return {
        "id": equipamento.id,
        "numero_patrimonio": equipamento.numero_patrimonio,
        "numero_serie": equipamento.numero_serie,
        "tipo": equipamento.tipo,
        "marca": equipamento.marca,
        "modelo": equipamento.modelo,
        "descricao": equipamento.descricao,
        "estado_conservacao": equipamento.estado_conservacao,
        "status": equipamento.status,
        "ativo": equipamento.ativo,
        "criado_em": equipamento.criado_em,
        "atualizado_em": equipamento.atualizado_em,
        "vinculo_atual": formatar_vinculo(vinculo) if vinculo else None,
        "acoes_permitidas": _acoes_permitidas(equipamento, vinculo),
    }


def formatar_detalhe(equipamento: Equipamento) -> dict:
    resultado = formatar_equipamento(equipamento)
    resultado["vinculos"] = [formatar_vinculo(vinculo) for vinculo in sorted(
        equipamento.vinculos, key=lambda item: item.vinculado_em, reverse=True
    )]
    resultado["eventos"] = [
        {
            "id": evento.id,
            "tipo": evento.tipo,
            "status_anterior": evento.status_anterior,
            "status_novo": evento.status_novo,
            "estado_conservacao": evento.estado_conservacao,
            "observacoes": evento.observacoes,
            "criado_por_nome": evento.criado_por.nome if evento.criado_por else "Sistema",
            "criado_em": evento.criado_em,
        }
        for evento in sorted(equipamento.eventos, key=lambda item: item.criado_em, reverse=True)
    ]
    return resultado


def buscar_equipamento(db: Session, equipamento_id: int, bloquear: bool = False) -> Equipamento:
    equipamento = patrimonios_repository.obter_equipamento(db, equipamento_id, bloquear)
    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    return equipamento


def _validar_identificadores(
    db: Session,
    patrimonio: str | None,
    serie: str | None,
    excluir_id: int | None = None,
) -> None:
    if patrimonio and patrimonios_repository.obter_por_patrimonio(db, patrimonio, excluir_id):
        raise HTTPException(status_code=400, detail="Número de patrimônio já cadastrado")
    if serie and patrimonios_repository.obter_por_serie(db, serie, excluir_id):
        raise HTTPException(status_code=400, detail="Número de série já cadastrado")


def _normalizar_identificadores(dados: dict) -> dict:
    for campo in ("numero_patrimonio", "numero_serie"):
        valor = dados.get(campo)
        if isinstance(valor, str):
            dados[campo] = valor.upper()
    return dados


def listar_equipamentos(
    db: Session,
    busca: str | None,
    tipo: str | None,
    status: str | None,
    ativo: bool | None,
    user_id: int | None,
    page: int,
    page_size: int,
) -> dict:
    if tipo and tipo not in TIPOS_EQUIPAMENTO:
        raise HTTPException(status_code=400, detail="Tipo de equipamento inválido")
    if status and status not in STATUS_EQUIPAMENTO:
        raise HTTPException(status_code=400, detail="Status de equipamento inválido")
    items, total = patrimonios_repository.listar_equipamentos(
        db, busca, tipo, status, ativo, user_id, (page - 1) * page_size, page_size
    )
    return {
        "items": [formatar_equipamento(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, math.ceil(total / page_size)),
    }


def criar_equipamento(db: Session, payload: EquipamentoCreate, current_user: User) -> dict:
    dados = _normalizar_identificadores(payload.model_dump())
    _validar_identificadores(db, dados["numero_patrimonio"], dados["numero_serie"])
    equipamento = Equipamento(**dados, status="disponivel", ativo=True)
    evento = EquipamentoEvento(
        equipamento=equipamento,
        tipo="criacao",
        status_novo="disponivel",
        estado_conservacao=payload.estado_conservacao,
        criado_por_id=current_user.id,
    )
    log = log_service.construir_log(
        current_user,
        acao="EQUIPAMENTO_CRIADO",
        detalhes=f"Equipamento {_texto_identificacao(equipamento)} cadastrado",
    )
    try:
        patrimonios_repository.salvar(db, equipamento, evento, log)
        patrimonios_repository.commit(db)
        db.refresh(equipamento)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Patrimônio ou número de série já cadastrado") from exc
    return formatar_equipamento(buscar_equipamento(db, equipamento.id))


def editar_equipamento(
    db: Session,
    equipamento_id: int,
    payload: EquipamentoUpdate,
    current_user: User,
) -> dict:
    equipamento = buscar_equipamento(db, equipamento_id, bloquear=True)
    if equipamento.status == "baixado":
        raise HTTPException(status_code=400, detail="Equipamento baixado não pode ser editado")

    dados = _normalizar_identificadores(payload.model_dump(exclude_unset=True))
    if (
        "tipo" in dados
        and dados["tipo"] != equipamento.tipo
        and equipamento.status in {"vinculado", "reservado"}
    ):
        raise HTTPException(
            status_code=400,
            detail="O tipo não pode ser alterado enquanto o equipamento estiver vinculado ou reservado",
        )
    _validar_identificadores(
        db,
        dados.get("numero_patrimonio", equipamento.numero_patrimonio),
        dados.get("numero_serie", equipamento.numero_serie),
        equipamento.id,
    )
    if dados.get("ativo") is False:
        if equipamento.status != "disponivel":
            raise HTTPException(
                status_code=400,
                detail="Somente equipamento disponível pode ser desativado",
            )
        if patrimonios_repository.obter_vinculo_ativo(db, equipamento.id):
            raise HTTPException(status_code=400, detail="Desvincule o equipamento antes de desativá-lo")

    alterados = []
    for campo, valor in dados.items():
        if getattr(equipamento, campo) != valor:
            setattr(equipamento, campo, valor)
            alterados.append(campo)
    if not alterados:
        return formatar_equipamento(equipamento)

    equipamento.atualizado_em = agora_utc()
    evento = EquipamentoEvento(
        equipamento_id=equipamento.id,
        tipo="edicao",
        status_novo=equipamento.status,
        estado_conservacao=equipamento.estado_conservacao,
        observacoes=f"Campos alterados: {', '.join(alterados)}",
        criado_por_id=current_user.id,
    )
    log = log_service.construir_log(
        current_user,
        acao="EQUIPAMENTO_EDITADO",
        detalhes=f"Equipamento {_texto_identificacao(equipamento)} editado ({', '.join(alterados)})",
    )
    try:
        patrimonios_repository.salvar(db, evento, log)
        patrimonios_repository.commit(db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Patrimônio ou número de série já cadastrado") from exc
    return formatar_equipamento(buscar_equipamento(db, equipamento.id))


def vincular_equipamento(
    db: Session,
    equipamento_id: int,
    payload: VinculoCreate,
    current_user: User,
) -> dict:
    equipamento = buscar_equipamento(db, equipamento_id, bloquear=True)
    usuario = patrimonios_repository.obter_usuario_bloqueado(db, payload.user_id)
    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=404, detail="Colaborador ativo não encontrado")
    if not equipamento.ativo or equipamento.status != "disponivel":
        raise HTTPException(status_code=400, detail="Equipamento não está disponível para vinculação")
    if patrimonios_repository.obter_vinculo_ativo(db, equipamento.id, bloquear=True):
        raise HTTPException(status_code=409, detail="Equipamento já possui um vínculo ativo")

    maquina_principal = equipamento.tipo in MAQUINAS_PRINCIPAIS
    if maquina_principal and patrimonios_repository.contar_maquinas_principais_ativas(db, usuario.id):
        if not payload.permitir_segunda_maquina:
            raise HTTPException(
                status_code=400,
                detail="Colaborador já possui uma máquina principal. Confirme e justifique a exceção.",
            )

    observacoes = payload.observacoes
    if payload.justificativa_excecao:
        observacoes = f"{observacoes + ' | ' if observacoes else ''}Exceção: {payload.justificativa_excecao}"
    vinculo = EquipamentoVinculo(
        equipamento_id=equipamento.id,
        user_id=usuario.id,
        vinculado_por_id=current_user.id,
        observacoes=observacoes,
        maquina_principal=maquina_principal,
        excecao_maquina_principal=maquina_principal and payload.permitir_segunda_maquina,
        justificativa_excecao=payload.justificativa_excecao,
    )
    anterior = equipamento.status
    equipamento.status = "vinculado"
    evento = EquipamentoEvento(
        equipamento_id=equipamento.id,
        tipo="vinculo",
        status_anterior=anterior,
        status_novo="vinculado",
        observacoes=f"Vinculado ao colaborador #{usuario.id}",
        criado_por_id=current_user.id,
    )
    log = log_service.construir_log(
        current_user,
        acao="EQUIPAMENTO_VINCULADO",
        detalhes=f"Equipamento {_texto_identificacao(equipamento)} vinculado ao usuário #{usuario.id}",
    )
    try:
        patrimonios_repository.salvar(db, vinculo, evento, log)
        patrimonios_repository.commit(db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Equipamento recebeu outro vínculo simultaneamente") from exc
    return formatar_equipamento(buscar_equipamento(db, equipamento.id))


def desvincular_equipamento(
    db: Session,
    equipamento_id: int,
    payload: DesvinculoCreate,
    current_user: User,
) -> dict:
    equipamento = buscar_equipamento(db, equipamento_id, bloquear=True)
    vinculo = patrimonios_repository.obter_vinculo_ativo(db, equipamento.id, bloquear=True)
    if not vinculo:
        raise HTTPException(status_code=400, detail="Equipamento não possui vínculo ativo")
    if patrimonios_repository.existe_autorizacao_entregue_em_aberto(db, equipamento.id):
        raise HTTPException(
            status_code=409,
            detail="Registre a devolução da autorização antes de encerrar este vínculo",
        )
    agora = agora_utc()
    vinculo.desvinculado_em = agora
    vinculo.desvinculado_por_id = current_user.id
    if payload.observacoes:
        vinculo.observacoes = f"{vinculo.observacoes + ' | ' if vinculo.observacoes else ''}{payload.observacoes}"
    equipamento.status = "disponivel"
    evento = EquipamentoEvento(
        equipamento_id=equipamento.id,
        tipo="desvinculo",
        status_anterior="vinculado",
        status_novo="disponivel",
        observacoes=f"Desvinculado do colaborador #{vinculo.user_id}",
        criado_por_id=current_user.id,
    )
    log = log_service.construir_log(
        current_user,
        acao="EQUIPAMENTO_DESVINCULADO",
        detalhes=f"Equipamento {_texto_identificacao(equipamento)} desvinculado do usuário #{vinculo.user_id}",
    )
    patrimonios_repository.salvar(db, evento, log)
    patrimonios_repository.commit(db)
    return formatar_equipamento(buscar_equipamento(db, equipamento.id))


def _alterar_status_operacional(
    db: Session,
    equipamento: Equipamento,
    status_novo: str,
    tipo_evento: str,
    observacoes: str,
    current_user: User,
    estado: str | None = None,
) -> dict:
    anterior = equipamento.status
    equipamento.status = status_novo
    if estado:
        equipamento.estado_conservacao = estado
    evento = EquipamentoEvento(
        equipamento_id=equipamento.id,
        tipo=tipo_evento,
        status_anterior=anterior,
        status_novo=status_novo,
        estado_conservacao=equipamento.estado_conservacao,
        observacoes=observacoes,
        criado_por_id=current_user.id,
    )
    log = log_service.construir_log(
        current_user,
        acao=f"EQUIPAMENTO_{tipo_evento.upper()}",
        detalhes=f"Equipamento {_texto_identificacao(equipamento)}: {anterior} -> {status_novo}",
    )
    patrimonios_repository.salvar(db, evento, log)
    patrimonios_repository.commit(db)
    return formatar_equipamento(buscar_equipamento(db, equipamento.id))


def iniciar_manutencao(
    db: Session, equipamento_id: int, payload: ManutencaoCreate, current_user: User
) -> dict:
    equipamento = buscar_equipamento(db, equipamento_id, bloquear=True)
    if not equipamento.ativo or equipamento.status != "disponivel":
        raise HTTPException(status_code=400, detail="Somente equipamento disponível pode entrar em manutenção")
    if patrimonios_repository.obter_vinculo_ativo(db, equipamento.id):
        raise HTTPException(status_code=400, detail="Desvincule o equipamento antes da manutenção")
    return _alterar_status_operacional(
        db, equipamento, "manutencao", "manutencao_iniciada", payload.observacoes,
        current_user, payload.estado_conservacao,
    )


def finalizar_manutencao(
    db: Session, equipamento_id: int, payload: ManutencaoCreate, current_user: User
) -> dict:
    equipamento = buscar_equipamento(db, equipamento_id, bloquear=True)
    if equipamento.status != "manutencao":
        raise HTTPException(status_code=400, detail="Equipamento não está em manutenção")
    return _alterar_status_operacional(
        db, equipamento, "disponivel", "manutencao_finalizada", payload.observacoes,
        current_user, payload.estado_conservacao,
    )


def baixar_equipamento(db: Session, equipamento_id: int, payload: BaixaCreate, current_user: User) -> dict:
    equipamento = buscar_equipamento(db, equipamento_id, bloquear=True)
    if equipamento.status == "baixado":
        return formatar_equipamento(equipamento)
    if equipamento.status == "reservado":
        raise HTTPException(status_code=400, detail="Equipamento reservado não pode ser baixado")
    if patrimonios_repository.obter_vinculo_ativo(db, equipamento.id):
        raise HTTPException(status_code=400, detail="Desvincule o equipamento antes da baixa")
    equipamento.ativo = False
    return _alterar_status_operacional(
        db, equipamento, "baixado", "baixado", payload.motivo, current_user
    )


def obter_detalhe(db: Session, equipamento_id: int) -> dict:
    return formatar_detalhe(buscar_equipamento(db, equipamento_id))


def meus_equipamentos(db: Session, current_user: User) -> list[dict]:
    return [formatar_equipamento(vinculo.equipamento) for vinculo in patrimonios_repository.listar_vinculos_ativos_usuario(
        db, current_user.id
    )]


def equipamentos_disponiveis(db: Session) -> list[dict]:
    return [formatar_equipamento(equipamento) for equipamento in patrimonios_repository.listar_disponiveis(db)]
