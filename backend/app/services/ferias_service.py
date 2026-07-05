from datetime import date, datetime, timedelta

import holidays as holidays_lib
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ferias import Ferias
from app.models.log import Log
from app.models.user import User
from app.repositories import ferias_repository
from app.schemas.ferias import FeriasAprovar, FeriasCreate, FeriasUpdate

LIMITE_SIMULTANEO_GLOBAL = 2
NOMES_DIA = ["segunda-feira", "terca-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sabado", "domingo"]


def feriados_br(anos: set) -> set:
    feriados: set = set()
    for ano in anos:
        feriados.update(holidays_lib.Brazil(years=ano).keys())
    return feriados


def primeiro_descanso_na_semana(ref: date, feriados: set) -> int:
    segunda = ref - timedelta(days=ref.weekday())
    for delta in range(5):
        if (segunda + timedelta(days=delta)) in feriados:
            return delta
    return 5


def verificar_regras_data(data_inicio: date, data_fim: date) -> None:
    hoje = date.today()

    if data_fim < data_inicio:
        raise HTTPException(status_code=400, detail="A data de fim nao pode ser anterior a data de inicio.")

    if data_inicio < hoje:
        raise HTTPException(status_code=400, detail="A data de inicio nao pode ser anterior a hoje.")

    feriados = feriados_br({data_inicio.year, data_fim.year})
    dia = data_inicio.weekday()

    if dia >= 5:
        raise HTTPException(status_code=400, detail=f"Ferias nao podem iniciar em {NOMES_DIA[dia]} (dia de descanso).")

    limite = primeiro_descanso_na_semana(data_inicio, feriados)
    bloqueados = {d for d in (limite - 2, limite - 1, limite) if 0 <= d <= 4}

    if dia in bloqueados:
        if limite < 5:
            segunda = data_inicio - timedelta(days=data_inicio.weekday())
            feriado_data = (segunda + timedelta(days=limite)).strftime("%d/%m/%Y")
            motivo = f"ha um feriado em {NOMES_DIA[limite]} ({feriado_data}) nesta semana, antecipando o periodo de descanso"
        else:
            motivo = "esta a menos de 48 horas do descanso semanal (sabado)"

        permitidos = [NOMES_DIA[d] for d in range(5) if d not in bloqueados]
        detalhe_permitidos = f" Dias permitidos nesta semana: {', '.join(permitidos)}." if permitidos else " Nao ha dia permitido nesta semana."
        raise HTTPException(status_code=400, detail=f"Ferias nao podem iniciar em {NOMES_DIA[dia]}: {motivo}.{detalhe_permitidos}")


def calcular_dias(data_inicio: date, data_fim: date) -> int:
    return (data_fim - data_inicio).days + 1


def get_ciclo_atual(data_admissao) -> tuple:
    today = date.today()

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


def calcular_saldo(db: Session, user: User, excluir_ferias_id: int | None = None) -> int:
    ciclo_inicio, ciclo_fim = get_ciclo_atual(user.data_admissao)
    ferias = ferias_repository.listar_ferias_para_saldo(db, user.id, ciclo_inicio, ciclo_fim, excluir_ferias_id)
    total_usado = sum(f.dias_usados for f in ferias)
    return user.dias_totais - total_usado


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
            detail=f"O periodo solicitado esta dentro de um {tipo_label}: '{bloqueio.motivo}' ({bloqueio.data_inicio} a {bloqueio.data_fim}).",
        )


def listar_feriados(year: int) -> list[dict]:
    feriados = holidays_lib.Brazil(years=year)
    return [{"data": str(d), "nome": nome} for d, nome in sorted(feriados.items())]


def minhas_ferias(db: Session, current_user: User) -> dict:
    ferias = ferias_repository.listar_ferias_por_usuario(db, current_user.id)
    ciclo_inicio, ciclo_fim = get_ciclo_atual(current_user.data_admissao)
    return {
        "ferias": [formatar_ferias(f) for f in ferias],
        "saldo": calcular_saldo(db, current_user),
        "ciclo_inicio": ciclo_inicio,
        "ciclo_fim": ciclo_fim,
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
    current_day = data_min
    while current_day <= data_max:
        if current_user.departamento_id:
            colegas_ids = {u.id for u in ferias_repository.listar_users_por_departamento(db, current_user.departamento_id)}
        else:
            colegas_ids = None

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
    verificar_regras_data(payload.data_inicio, payload.data_fim)
    dias_solicitados = calcular_dias(payload.data_inicio, payload.data_fim)
    verificar_bloqueio_datas(db, payload.data_inicio, payload.data_fim)

    if not payload.ferias_acordo:
        if verificar_sobreposicao_departamento(db, current_user, payload.data_inicio, payload.data_fim):
            limite = get_limite_departamento(current_user, db)
            raise HTTPException(status_code=400, detail=f"Limite de {limite} colaborador(es) simultaneo(s) no departamento ja atingido no periodo solicitado.")

        saldo = calcular_saldo(db, current_user)
        if saldo < dias_solicitados:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Voce possui {saldo} dia(s) disponivel(is) no ciclo atual, mas solicitou {dias_solicitados}.")

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
    log = Log(user_id=current_user.id, acao=acao, detalhes=f"Periodo: {payload.data_inicio} a {payload.data_fim} ({dias_solicitados} dias) - status: {novo_status}")
    ferias_repository.salvar_ferias_com_log(db, nova_ferias, log)
    return formatar_ferias(nova_ferias)


def buscar_ferias(db: Session, ferias_id: int) -> Ferias:
    ferias = ferias_repository.obter_ferias_por_id(db, ferias_id)
    if not ferias:
        raise HTTPException(status_code=404, detail="Ferias nao encontradas")
    return ferias


def aprovar_ferias(db: Session, ferias_id: int, current_user: User) -> dict:
    ferias = buscar_ferias(db, ferias_id)
    if ferias.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Solicitacao nao esta pendente (status atual: {ferias.status})")

    owner = ferias_repository.obter_user_por_id(db, ferias.user_id)
    if not ferias.ferias_acordo:
        if verificar_sobreposicao_departamento(db, owner, ferias.data_inicio, ferias.data_fim, excluir_ferias_id=ferias_id):
            limite = get_limite_departamento(owner, db)
            raise HTTPException(status_code=400, detail=f"Nao e possivel aprovar: limite de {limite} simultaneo(s) no departamento seria excedido.")

    ferias.status = "aprovada"
    ferias.motivo_rejeicao = None
    ferias.aprovado_por_id = current_user.id
    ferias.aprovado_em = datetime.utcnow()
    ferias.rejeitado_por_id = None
    ferias.rejeitado_em = None

    log = Log(user_id=current_user.id, acao="FERIAS_APROVADA", detalhes=f"Ferias #{ferias_id} de {owner.nome} aprovadas ({ferias.data_inicio} a {ferias.data_fim})")
    ferias_repository.atualizar_ferias_com_log(db, ferias, log)
    return formatar_ferias(ferias)


def rejeitar_ferias(db: Session, ferias_id: int, payload: FeriasAprovar, current_user: User) -> dict:
    ferias = buscar_ferias(db, ferias_id)
    if ferias.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Solicitacao nao esta pendente (status atual: {ferias.status})")

    owner = ferias_repository.obter_user_por_id(db, ferias.user_id)
    ferias.status = "rejeitada"
    ferias.motivo_rejeicao = payload.motivo_rejeicao
    ferias.rejeitado_por_id = current_user.id
    ferias.rejeitado_em = datetime.utcnow()
    ferias.aprovado_por_id = None
    ferias.aprovado_em = None

    log = Log(user_id=current_user.id, acao="FERIAS_REJEITADA", detalhes=f"Ferias #{ferias_id} de {owner.nome} rejeitadas. Motivo: {payload.motivo_rejeicao or 'nao informado'}")
    ferias_repository.atualizar_ferias_com_log(db, ferias, log)
    return formatar_ferias(ferias)


def editar_ferias(db: Session, ferias_id: int, payload: FeriasUpdate, current_user: User) -> dict:
    ferias = buscar_ferias(db, ferias_id)

    if current_user.role != "admin":
        if ferias.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Sem permissao para editar ferias de outro usuario")
        if ferias.status not in ("pendente",):
            raise HTTPException(status_code=403, detail="Apenas ferias pendentes podem ser editadas pelo colaborador")

    owner = ferias_repository.obter_user_por_id(db, ferias.user_id)
    nova_inicio = payload.data_inicio if payload.data_inicio is not None else ferias.data_inicio
    nova_fim = payload.data_fim if payload.data_fim is not None else ferias.data_fim

    verificar_regras_data(nova_inicio, nova_fim)
    dias_solicitados = calcular_dias(nova_inicio, nova_fim)
    novo_acordo = payload.ferias_acordo if payload.ferias_acordo is not None else ferias.ferias_acordo

    if not novo_acordo:
        if verificar_sobreposicao_departamento(db, owner, nova_inicio, nova_fim, excluir_ferias_id=ferias_id):
            limite = get_limite_departamento(owner, db)
            raise HTTPException(status_code=400, detail=f"Limite de {limite} simultaneo(s) no departamento seria excedido.")

        saldo = calcular_saldo(db, owner, excluir_ferias_id=ferias_id)
        if saldo < dias_solicitados:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Disponivel: {saldo} dia(s), solicitado: {dias_solicitados}.")

    ferias.data_inicio = nova_inicio
    ferias.data_fim = nova_fim
    ferias.dias_usados = dias_solicitados
    ferias.ferias_acordo = novo_acordo

    if current_user.role == "admin":
        if payload.status is not None:
            if payload.status not in ("pendente", "aprovada", "rejeitada"):
                raise HTTPException(status_code=400, detail="Status invalido")
            ferias.status = payload.status
        if payload.motivo_rejeicao is not None:
            ferias.motivo_rejeicao = payload.motivo_rejeicao

    log = Log(user_id=current_user.id, acao="FERIAS_EDITADA", detalhes=f"Ferias #{ferias_id} de {owner.nome} alteradas para {nova_inicio} a {nova_fim} ({dias_solicitados} dias)")
    ferias_repository.atualizar_ferias_com_log(db, ferias, log)
    return formatar_ferias(ferias)


def cancelar_ferias(db: Session, ferias_id: int, current_user: User) -> None:
    ferias = buscar_ferias(db, ferias_id)
    if current_user.role != "admin" and ferias.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissao para cancelar ferias de outro usuario")

    owner = ferias_repository.obter_user_por_id(db, ferias.user_id)
    detalhes = f"Ferias #{ferias_id} de {owner.nome if owner else '?'} ({ferias.data_inicio} a {ferias.data_fim}) canceladas"
    log = Log(user_id=current_user.id, acao="FERIAS_CANCELADA", detalhes=detalhes)
    ferias_repository.excluir_ferias_com_log(db, ferias, log)
