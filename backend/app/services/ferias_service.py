from datetime import date, datetime, timedelta

import holidays as holidays_lib
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.timezone import hoje_sao_paulo
from app.models.ferias import Ferias
from app.models.log import Log
from app.models.saldo_ferias import SaldoFeriasMovimento
from app.models.user import User
from app.repositories import ferias_repository
from app.schemas.ferias import FeriasAprovar, FeriasCreate, FeriasUpdate
from app.services import log_service

LIMITE_SIMULTANEO_GLOBAL = 2
NOMES_DIA = ["segunda-feira", "terca-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sabado", "domingo"]


def bloquear_regras_ferias(db: Session, user: User) -> None:
    """Serializa alterações que disputam saldo ou limite do mesmo departamento."""
    dialect = getattr(getattr(db, "bind", None), "dialect", None)
    if getattr(dialect, "name", None) != "postgresql":
        return
    chaves = sorted((1_000_000 + user.id, 2_000_000 + (user.departamento_id or 0)))
    for chave in chaves:
        db.execute(text("SELECT pg_advisory_xact_lock(:chave)"), {"chave": chave})


DIAS_INICIO_PERMITIDOS = (0, 1, 2)  # segunda, terca, quarta-feira


def feriados_br(anos: set) -> set:
    feriados: set = set()
    for ano in anos:
        feriados.update(holidays_lib.Brazil(years=ano).keys())
    return feriados


def feriado_bloqueante(data_inicio: date, feriados: set) -> tuple[date, int] | None:
    """Retorna (data_do_feriado, offset) se `data_inicio` for o proprio feriado
    ou cair nos dois dias imediatamente anteriores a ele."""
    for offset in (0, 1, 2):
        candidato = data_inicio + timedelta(days=offset)
        if candidato in feriados:
            return candidato, offset
    return None


def verificar_regras_data(data_inicio: date, data_fim: date) -> None:
    hoje = hoje_sao_paulo()

    if data_fim < data_inicio:
        raise HTTPException(status_code=400, detail="A data de fim não pode ser anterior à data de início.")

    if data_inicio < hoje:
        raise HTTPException(status_code=400, detail="A data de início não pode ser anterior a hoje.")

    dia = data_inicio.weekday()
    permitidos = [NOMES_DIA[d] for d in DIAS_INICIO_PERMITIDOS]

    if dia not in DIAS_INICIO_PERMITIDOS:
        motivo = "dia de descanso semanal remunerado (DSR)" if dia >= 5 else "as férias somente podem iniciar às segunda, terça ou quarta-feira"
        raise HTTPException(
            status_code=400,
            detail=f"Férias não podem iniciar em {NOMES_DIA[dia]}: {motivo}. Dias permitidos: {', '.join(permitidos)}.",
        )

    feriados = feriados_br({data_inicio.year, data_inicio.year + 1})
    resultado = feriado_bloqueante(data_inicio, feriados)

    if resultado:
        feriado_data, offset = resultado
        feriado_str = feriado_data.strftime("%d/%m/%Y")
        motivo = (
            f"é um feriado ({feriado_str})"
            if offset == 0
            else f"está nos dois dias imediatamente anteriores ao feriado de {feriado_str}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Férias não podem iniciar em {NOMES_DIA[dia]}: {motivo}. Dias permitidos: {', '.join(permitidos)}.",
        )


def calcular_dias(data_inicio: date, data_fim: date) -> int:
    return (data_fim - data_inicio).days + 1


def get_ciclo_atual(data_admissao) -> tuple:
    today = hoje_sao_paulo()

    if not data_admissao:
        return date(today.year, 1, 1), date(today.year, 12, 31)

    ano = today.year
    try:
        ciclo_inicio = data_admissao.replace(year=ano)
    except ValueError:
        ciclo_inicio = data_admissao.replace(year=ano, day=28)

    if ciclo_inicio > today:
        try:
            ciclo_inicio = data_admissao.replace(year=ano - 1)
        except ValueError:
            ciclo_inicio = data_admissao.replace(year=ano - 1, day=28)

    try:
        ciclo_fim = data_admissao.replace(year=ciclo_inicio.year + 1) - timedelta(days=1)
    except ValueError:
        ciclo_fim = data_admissao.replace(year=ciclo_inicio.year + 1, day=28) - timedelta(days=1)

    return ciclo_inicio, ciclo_fim


def get_limite_departamento(user: User, db: Session) -> int:
    if user.departamento_id:
        dep = ferias_repository.obter_departamento_por_id(db, user.departamento_id)
        if dep:
            return dep.limite_simultaneo
    return LIMITE_SIMULTANEO_GLOBAL


def verificar_sobreposicao_departamento(
    db: Session,
    user: User,
    data_inicio: date,
    data_fim: date,
    excluir_ferias_id: int | None = None,
) -> bool:
    limite = get_limite_departamento(user, db)
    query = ferias_repository.listar_ferias_conflitantes(db, user.id, data_inicio, data_fim, excluir_ferias_id)

    if user.departamento_id:
        colegas_ids = [u.id for u in ferias_repository.listar_users_por_departamento(db, user.departamento_id)]
        query = query.filter(Ferias.user_id.in_(colegas_ids))

    conflitos = query.all()

    if len(conflitos) >= limite:
        current = data_inicio
        while current <= data_fim:
            count = sum(1 for f in conflitos if f.data_inicio <= current <= f.data_fim)
            if count >= limite:
                return True
            current += timedelta(days=1)

    return False


def _somar_anos(data: date, anos: int) -> date:
    try:
        return data.replace(year=data.year + anos)
    except ValueError:
        return data.replace(year=data.year + anos, day=28)


def proxima_concessao_apos(data_admissao: date | None, referencia: date | None = None) -> date | None:
    if not data_admissao:
        return None
    referencia = referencia or hoje_sao_paulo()
    candidata = _somar_anos(data_admissao, max(referencia.year - data_admissao.year, 0))
    if candidata <= referencia:
        candidata = _somar_anos(candidata, 1)
    return candidata


def registrar_saldo_inicial(
    db: Session,
    user: User,
    saldo_dias: int,
    criado_por_id: int | None = None,
    commit: bool = True,
) -> None:
    chave = f"saldo-inicial:{user.id}"
    if ferias_repository.obter_movimento_por_chave(db, chave):
        return
    db.add(SaldoFeriasMovimento(
        user_id=user.id,
        tipo="saldo_inicial",
        quantidade_dias=saldo_dias,
        data_referencia=hoje_sao_paulo(),
        motivo="Saldo informado na implantação/cadastro do colaborador.",
        criado_por_id=criado_por_id,
        chave_idempotencia=chave,
    ))
    if commit:
        db.commit()
    else:
        db.flush()


def sincronizar_creditos_anuais(
    db: Session,
    user: User,
    hoje: date | None = None,
    commit: bool = True,
) -> int:
    hoje = hoje or hoje_sao_paulo()
    if getattr(user, "proxima_concessao_ferias", None) is None:
        user.proxima_concessao_ferias = proxima_concessao_apos(user.data_admissao, hoje)
        if user.proxima_concessao_ferias is not None and commit:
            db.commit()
        return 0

    criados = 0
    avancou = False
    while user.proxima_concessao_ferias <= hoje:
        referencia = user.proxima_concessao_ferias
        chave = f"credito-anual:{user.id}:{referencia.isoformat()}"
        if not ferias_repository.obter_movimento_por_chave(db, chave):
            db.add(SaldoFeriasMovimento(
                user_id=user.id,
                tipo="credito_anual",
                quantidade_dias=user.dias_totais,
                data_referencia=referencia,
                motivo=f"Crédito anual de férias referente a {referencia.strftime('%d/%m/%Y')}.",
                criado_por_id=None,
                chave_idempotencia=chave,
            ))
            if not getattr(user, "is_sistema", False):
                db.add(Log(
                    user_id=user.id,
                    acao="SALDO_FERIAS_CREDITADO",
                    detalhes=f"Crédito automático de {user.dias_totais} dia(s) em {referencia.strftime('%d/%m/%Y')}.",
                ))
            criados += 1
        user.proxima_concessao_ferias = _somar_anos(referencia, 1)
        avancou = True
    if avancou and commit:
        db.commit()
    elif avancou:
        db.flush()
    return criados


def garantir_saldo_atualizado(
    db: Session,
    user: User,
    criado_por_id: int | None = None,
    commit: bool = True,
) -> None:
    """Comando idempotente usado apenas em operações que podem escrever."""
    bloquear_regras_ferias(db, user)
    if not ferias_repository.listar_movimentos_saldo(db, user.id):
        registrar_saldo_inicial(
            db,
            user,
            user.saldo_manual_dias if user.saldo_manual_dias is not None else 0,
            criado_por_id,
            commit=False,
        )
    sincronizar_creditos_anuais(db, user, commit=False)
    if commit:
        db.commit()


def ajustar_saldo(
    db: Session,
    user: User,
    novo_saldo: int,
    motivo: str,
    current_user: User,
    commit: bool = True,
) -> None:
    saldo_atual = calcular_saldo(db, user)
    diferenca = novo_saldo - saldo_atual
    if diferenca == 0:
        return
    db.add(SaldoFeriasMovimento(
        user_id=user.id,
        tipo="ajuste_manual",
        quantidade_dias=diferenca,
        data_referencia=hoje_sao_paulo(),
        motivo=motivo,
        criado_por_id=current_user.id,
        chave_idempotencia=f"ajuste:{user.id}:{datetime.utcnow().isoformat()}",
    ))
    log = log_service.construir_log(
        current_user,
        acao="SALDO_FERIAS_AJUSTADO",
        detalhes=(
            f"Saldo de {user.nome} ajustado de {saldo_atual} para {novo_saldo} dia(s). "
            f"Motivo: {motivo}"
        ),
    )
    if log is not None:
        db.add(log)
    if commit:
        db.commit()
    else:
        db.flush()


def calcular_extrato_saldo(db: Session, user: User, excluir_ferias_id: int | None = None) -> dict:
    """Consulta pura do saldo desde a implantacao."""
    movimentos = ferias_repository.listar_movimentos_saldo(db, user.id)
    if not movimentos:
        ferias_contabeis = []
    else:
        marco = movimentos[0].criado_em
        ferias_contabeis = ferias_repository.listar_ferias_para_saldo_desde(
            db, user.id, marco, excluir_ferias_id
        )
    dias_usados_total = sum(f.dias_usados for f in ferias_contabeis)
    total_movimentos = sum(m.quantidade_dias for m in movimentos)

    return {
        "saldo": total_movimentos - dias_usados_total,
        "dias_direito_total": total_movimentos,
        "dias_usados_total": dias_usados_total,
        "anos_completos": 0,
        "dias_vencidos_total": 0,
        "vencidas": [],
        "movimentos": movimentos,
    }


def calcular_saldo(db: Session, user: User, excluir_ferias_id: int | None = None) -> int:
    return calcular_extrato_saldo(db, user, excluir_ferias_id)["saldo"]


def formatar_ferias(ferias: Ferias) -> dict:
    return {
        "id": ferias.id,
        "user_id": ferias.user_id,
        "nome_usuario": ferias.usuario.nome if ferias.usuario else None,
        "cor_usuario": ferias.usuario.cor if ferias.usuario else None,
        "data_inicio": ferias.data_inicio,
        "data_fim": ferias.data_fim,
        "dias_usados": ferias.dias_usados,
        "status": ferias.status,
        "ferias_acordo": ferias.ferias_acordo,
        "motivo_rejeicao": ferias.motivo_rejeicao,
        "criado_em": ferias.criado_em,
        "aprovado_por_id": ferias.aprovado_por_id,
        "aprovado_por_nome": ferias.aprovado_por.nome if ferias.aprovado_por else None,
        "aprovado_em": ferias.aprovado_em,
        "rejeitado_por_id": ferias.rejeitado_por_id,
        "rejeitado_por_nome": ferias.rejeitado_por.nome if ferias.rejeitado_por else None,
        "rejeitado_em": ferias.rejeitado_em,
    }


def verificar_bloqueio_datas(db: Session, data_inicio: date, data_fim: date) -> None:
    bloqueio = ferias_repository.obter_bloqueio_sobreposto(db, data_inicio, data_fim)
    if bloqueio:
        tipo_label = "recesso" if bloqueio.tipo == "recesso" else "bloqueio"
        raise HTTPException(
            status_code=400,
            detail=f"O período solicitado está dentro de um {tipo_label}: '{bloqueio.motivo}' ({bloqueio.data_inicio} a {bloqueio.data_fim}).",
        )


def verificar_sobreposicao_usuario(
    db: Session,
    user_id: int,
    data_inicio: date,
    data_fim: date,
    excluir_ferias_id: int | None = None,
) -> None:
    existente = ferias_repository.obter_ferias_usuario_sobreposta(
        db,
        user_id,
        data_inicio,
        data_fim,
        excluir_ferias_id,
    )
    if existente:
        raise HTTPException(
            status_code=409,
            detail=(
                "O período se sobrepõe a outra solicitação de férias "
                f"({existente.data_inicio} a {existente.data_fim})."
            ),
        )


def listar_feriados(year: int) -> list[dict]:
    feriados = holidays_lib.Brazil(years=year)
    return [{"data": str(d), "nome": nome} for d, nome in sorted(feriados.items())]


def minhas_ferias(db: Session, current_user: User) -> dict:
    ferias = ferias_repository.listar_ferias_por_usuario(db, current_user.id)
    ciclo_inicio, ciclo_fim = get_ciclo_atual(current_user.data_admissao)
    extrato = calcular_extrato_saldo(db, current_user)
    return {
        "ferias": [formatar_ferias(f) for f in ferias],
        "saldo": extrato["saldo"],
        "ciclo_inicio": ciclo_inicio,
        "ciclo_fim": ciclo_fim,
        "dias_usados_total": extrato["dias_usados_total"],
        "dias_direito_total": extrato["dias_direito_total"],
        "dias_vencidos": extrato["vencidas"],
        "movimentos_saldo": [
            {
                "tipo": movimento.tipo,
                "quantidade_dias": movimento.quantidade_dias,
                "data_referencia": movimento.data_referencia,
                "motivo": movimento.motivo,
                "criado_em": movimento.criado_em,
            }
            for movimento in reversed(extrato["movimentos"])
        ],
        "proxima_concessao_ferias": current_user.proxima_concessao_ferias,
    }


def ferias_pendentes(db: Session) -> list[dict]:
    return [formatar_ferias(f) for f in ferias_repository.listar_ferias_pendentes(db)]


def todas_ferias(db: Session) -> list[dict]:
    return [formatar_ferias(f) for f in ferias_repository.listar_todas_ferias(db)]


def disponibilidade(db: Session, current_user: User) -> dict:
    todas_ferias = ferias_repository.listar_ferias_aprovadas(db)
    user_ids = {f.user_id for f in todas_ferias}
    users_by_id = {u.id: u for u in (ferias_repository.obter_user_por_id(db, user_id) for user_id in user_ids) if u}

    ferias_marcadas = [
        {
            "id": f.id,
            "user_id": f.user_id,
            "nome": users_by_id.get(f.user_id).nome if users_by_id.get(f.user_id) else "Colaborador",
            "cor": users_by_id.get(f.user_id).cor if users_by_id.get(f.user_id) else None,
            "data_inicio": f.data_inicio,
            "data_fim": f.data_fim,
            "dias_usados": f.dias_usados,
            "ferias_acordo": f.ferias_acordo,
        }
        for f in todas_ferias
    ]

    bloqueios_fmt = [
        {"id": b.id, "data_inicio": b.data_inicio, "data_fim": b.data_fim, "motivo": b.motivo, "tipo": b.tipo}
        for b in ferias_repository.listar_bloqueios(db)
    ]

    if not todas_ferias:
        return {"periodos_bloqueados": [], "ferias_marcadas": [], "bloqueios_manuais": bloqueios_fmt}

    limite = get_limite_departamento(current_user, db)
    data_min = min(f.data_inicio for f in todas_ferias)
    data_max = max(f.data_fim for f in todas_ferias)

    bloqueados = []
    colegas_ids = (
        {u.id for u in ferias_repository.listar_users_por_departamento(db, current_user.departamento_id)}
        if current_user.departamento_id
        else None
    )
    current_day = data_min
    while current_day <= data_max:
        count = sum(
            1
            for f in todas_ferias
            if f.data_inicio <= current_day <= f.data_fim and (colegas_ids is None or f.user_id in colegas_ids)
        )
        if count >= limite:
            bloqueados.append(current_day)
        current_day += timedelta(days=1)

    periodos: list[dict] = []
    if bloqueados:
        inicio = bloqueados[0]
        anterior = bloqueados[0]
        for dia in bloqueados[1:]:
            if (dia - anterior).days == 1:
                anterior = dia
            else:
                periodos.append({"data_inicio": inicio, "data_fim": anterior})
                inicio = dia
                anterior = dia
        periodos.append({"data_inicio": inicio, "data_fim": anterior})

    return {"periodos_bloqueados": periodos, "ferias_marcadas": ferias_marcadas, "bloqueios_manuais": bloqueios_fmt}


def registrar_ferias(db: Session, payload: FeriasCreate, current_user: User) -> dict:
    bloquear_regras_ferias(db, current_user)
    garantir_saldo_atualizado(db, current_user, current_user.id, commit=False)
    verificar_regras_data(payload.data_inicio, payload.data_fim)
    dias_solicitados = calcular_dias(payload.data_inicio, payload.data_fim)
    verificar_bloqueio_datas(db, payload.data_inicio, payload.data_fim)
    verificar_sobreposicao_usuario(
        db,
        current_user.id,
        payload.data_inicio,
        payload.data_fim,
    )

    if payload.ferias_acordo and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Férias por acordo só podem ser registradas por um administrador",
        )

    if not payload.ferias_acordo:
        if verificar_sobreposicao_departamento(db, current_user, payload.data_inicio, payload.data_fim):
            limite = get_limite_departamento(current_user, db)
            raise HTTPException(status_code=400, detail=f"Limite de {limite} colaborador(es) simultâneo(s) no departamento já atingido no período solicitado.")

        saldo = calcular_saldo(db, current_user)
        if saldo < dias_solicitados:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Você possui {saldo} dia(s) disponível(is) no ciclo atual, mas solicitou {dias_solicitados}.")

    novo_status = "aprovada" if current_user.role == "admin" else "pendente"
    nova_ferias = Ferias(
        user_id=current_user.id,
        data_inicio=payload.data_inicio,
        data_fim=payload.data_fim,
        dias_usados=dias_solicitados,
        status=novo_status,
        ferias_acordo=payload.ferias_acordo,
    )
    acao = "FERIAS_REGISTRADA" if novo_status == "aprovada" else "FERIAS_SOLICITADA"
    log = log_service.construir_log(current_user, acao=acao, detalhes=f"Período: {payload.data_inicio} a {payload.data_fim} ({dias_solicitados} dias) - status: {novo_status}")
    ferias_repository.salvar_ferias_com_log(db, nova_ferias, log)
    return formatar_ferias(nova_ferias)


def buscar_ferias_para_atualizar(db: Session, ferias_id: int) -> Ferias:
    ferias = ferias_repository.obter_ferias_por_id_para_atualizar(db, ferias_id)
    if not ferias:
        raise HTTPException(status_code=404, detail="Férias não encontradas")
    return ferias


def aprovar_ferias(db: Session, ferias_id: int, current_user: User) -> dict:
    ferias = buscar_ferias_para_atualizar(db, ferias_id)
    if ferias.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Solicitação não está pendente (status atual: {ferias.status})")

    owner = ferias_repository.obter_user_por_id(db, ferias.user_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    bloquear_regras_ferias(db, owner)
    garantir_saldo_atualizado(db, owner, current_user.id, commit=False)
    verificar_regras_data(ferias.data_inicio, ferias.data_fim)
    verificar_bloqueio_datas(db, ferias.data_inicio, ferias.data_fim)
    verificar_sobreposicao_usuario(
        db,
        owner.id,
        ferias.data_inicio,
        ferias.data_fim,
        excluir_ferias_id=ferias_id,
    )
    if not ferias.ferias_acordo:
        if verificar_sobreposicao_departamento(db, owner, ferias.data_inicio, ferias.data_fim, excluir_ferias_id=ferias_id):
            limite = get_limite_departamento(owner, db)
            raise HTTPException(status_code=400, detail=f"Não é possível aprovar: limite de {limite} simultâneo(s) no departamento seria excedido.")
        saldo = calcular_saldo(db, owner, excluir_ferias_id=ferias_id)
        if saldo < ferias.dias_usados:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Não é possível aprovar: saldo disponível de {saldo} dia(s), "
                    f"solicitado de {ferias.dias_usados} dia(s)."
                ),
            )

    ferias.status = "aprovada"
    ferias.motivo_rejeicao = None
    ferias.aprovado_por_id = current_user.id
    ferias.aprovado_em = datetime.utcnow()
    ferias.rejeitado_por_id = None
    ferias.rejeitado_em = None

    log = log_service.construir_log(current_user, acao="FERIAS_APROVADA", detalhes=f"Férias #{ferias_id} de {owner.nome} aprovadas ({ferias.data_inicio} a {ferias.data_fim})")
    ferias_repository.atualizar_ferias_com_log(db, ferias, log)
    return formatar_ferias(ferias)


def rejeitar_ferias(db: Session, ferias_id: int, payload: FeriasAprovar, current_user: User) -> dict:
    ferias = buscar_ferias_para_atualizar(db, ferias_id)
    if ferias.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Solicitação não está pendente (status atual: {ferias.status})")

    owner = ferias_repository.obter_user_por_id(db, ferias.user_id)
    ferias.status = "rejeitada"
    ferias.motivo_rejeicao = payload.motivo_rejeicao
    ferias.rejeitado_por_id = current_user.id
    ferias.rejeitado_em = datetime.utcnow()
    ferias.aprovado_por_id = None
    ferias.aprovado_em = None

    log = log_service.construir_log(current_user, acao="FERIAS_REJEITADA", detalhes=f"Férias #{ferias_id} de {owner.nome} rejeitadas. Motivo: {payload.motivo_rejeicao or 'não informado'}")
    ferias_repository.atualizar_ferias_com_log(db, ferias, log)
    return formatar_ferias(ferias)


def editar_ferias(db: Session, ferias_id: int, payload: FeriasUpdate, current_user: User) -> dict:
    ferias = buscar_ferias_para_atualizar(db, ferias_id)

    if current_user.role != "admin":
        if ferias.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Sem permissão para editar férias de outro usuário")
        if ferias.status not in ("pendente",):
            raise HTTPException(status_code=403, detail="Apenas férias pendentes podem ser editadas pelo colaborador")

    owner = ferias_repository.obter_user_por_id(db, ferias.user_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    bloquear_regras_ferias(db, owner)
    garantir_saldo_atualizado(db, owner, current_user.id, commit=False)
    nova_inicio = payload.data_inicio if payload.data_inicio is not None else ferias.data_inicio
    nova_fim = payload.data_fim if payload.data_fim is not None else ferias.data_fim

    verificar_regras_data(nova_inicio, nova_fim)
    verificar_bloqueio_datas(db, nova_inicio, nova_fim)
    verificar_sobreposicao_usuario(
        db,
        owner.id,
        nova_inicio,
        nova_fim,
        excluir_ferias_id=ferias_id,
    )
    dias_solicitados = calcular_dias(nova_inicio, nova_fim)
    novo_acordo = payload.ferias_acordo if payload.ferias_acordo is not None else ferias.ferias_acordo
    if novo_acordo and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Férias por acordo só podem ser definidas por um administrador",
        )

    if not novo_acordo:
        if verificar_sobreposicao_departamento(db, owner, nova_inicio, nova_fim, excluir_ferias_id=ferias_id):
            limite = get_limite_departamento(owner, db)
            raise HTTPException(status_code=400, detail=f"Limite de {limite} simultâneo(s) no departamento seria excedido.")

        saldo = calcular_saldo(db, owner, excluir_ferias_id=ferias_id)
        if saldo < dias_solicitados:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Disponível: {saldo} dia(s), solicitado: {dias_solicitados}.")

    ferias.data_inicio = nova_inicio
    ferias.data_fim = nova_fim
    ferias.dias_usados = dias_solicitados
    ferias.ferias_acordo = novo_acordo

    log = log_service.construir_log(current_user, acao="FERIAS_EDITADA", detalhes=f"Férias #{ferias_id} de {owner.nome} alteradas para {nova_inicio} a {nova_fim} ({dias_solicitados} dias)")
    ferias_repository.atualizar_ferias_com_log(db, ferias, log)
    return formatar_ferias(ferias)


def cancelar_ferias(db: Session, ferias_id: int, current_user: User) -> None:
    ferias = buscar_ferias_para_atualizar(db, ferias_id)
    if current_user.role != "admin" and ferias.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para cancelar férias de outro usuário")

    owner = ferias_repository.obter_user_por_id(db, ferias.user_id)
    detalhes = f"Férias #{ferias_id} de {owner.nome if owner else '?'} ({ferias.data_inicio} a {ferias.data_fim}) canceladas"
    log = log_service.construir_log(current_user, acao="FERIAS_CANCELADA", detalhes=detalhes)
    ferias_repository.excluir_ferias_com_log(db, ferias, log)
