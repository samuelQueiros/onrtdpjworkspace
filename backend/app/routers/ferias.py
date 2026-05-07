from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.ferias import Ferias
from app.models.log import Log
from app.models.departamento import Departamento
from app.schemas.ferias import FeriasCreate, FeriasUpdate, FeriasAprovar
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/ferias", tags=["Férias"])

LIMITE_SIMULTANEO_GLOBAL = 2  # fallback quando sem departamento


# ── Utilitários ──────────────────────────────────────────────────────────────

def calcular_dias(data_inicio: date, data_fim: date) -> int:
    return (data_fim - data_inicio).days + 1


def get_ciclo_atual(data_admissao) -> tuple:
    """Retorna (ciclo_inicio, ciclo_fim) baseado na data de admissão."""
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
        dep = db.query(Departamento).filter(Departamento.id == user.departamento_id).first()
        if dep:
            return dep.limite_simultaneo
    return LIMITE_SIMULTANEO_GLOBAL


def verificar_sobreposicao_departamento(
    db: Session,
    user: User,
    data_inicio: date,
    data_fim: date,
    excluir_ferias_id: int = None,
) -> bool:
    """
    Verifica se o limite simultâneo do departamento (ou global) seria excedido.
    Conta apenas férias APROVADAS de outros usuários do mesmo departamento (ou todos, se sem depto).
    """
    limite = get_limite_departamento(user, db)

    query = db.query(Ferias).filter(
        Ferias.data_inicio <= data_fim,
        Ferias.data_fim >= data_inicio,
        Ferias.status == "aprovada",
        Ferias.user_id != user.id,
    )

    if excluir_ferias_id:
        query = query.filter(Ferias.id != excluir_ferias_id)

    # Filtrar pelo mesmo departamento quando houver
    if user.departamento_id:
        colegas_ids = [
            u.id for u in db.query(User).filter(User.departamento_id == user.departamento_id).all()
        ]
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


def calcular_saldo(db: Session, user: User, excluir_ferias_id: int = None) -> int:
    """
    Retorna saldo restante no ciclo atual.
    Férias por acordo não contam. Apenas férias aprovadas e pendentes no ciclo.
    """
    ciclo_inicio, ciclo_fim = get_ciclo_atual(user.data_admissao)

    query = db.query(Ferias).filter(
        Ferias.user_id == user.id,
        Ferias.ferias_acordo == False,  # noqa: E712
        Ferias.status.in_(["aprovada", "pendente"]),
        Ferias.data_inicio >= ciclo_inicio,
        Ferias.data_inicio <= ciclo_fim,
    )
    if excluir_ferias_id:
        query = query.filter(Ferias.id != excluir_ferias_id)

    total_usado = sum(f.dias_usados for f in query.all())
    return user.dias_totais - total_usado


def _fmt_ferias(f: Ferias) -> dict:
    return {
        "id": f.id,
        "user_id": f.user_id,
        "nome_usuario": f.usuario.nome if f.usuario else None,
        "data_inicio": f.data_inicio,
        "data_fim": f.data_fim,
        "dias_usados": f.dias_usados,
        "status": f.status,
        "ferias_acordo": f.ferias_acordo,
        "motivo_rejeicao": f.motivo_rejeicao,
        "criado_em": f.criado_em,
    }


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/me")
def minhas_ferias(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ferias = db.query(Ferias).filter(Ferias.user_id == current_user.id).order_by(Ferias.criado_em.desc()).all()
    ciclo_inicio, ciclo_fim = get_ciclo_atual(current_user.data_admissao)
    saldo = calcular_saldo(db, current_user)
    return {
        "ferias": [_fmt_ferias(f) for f in ferias],
        "saldo": saldo,
        "ciclo_inicio": ciclo_inicio,
        "ciclo_fim": ciclo_fim,
    }


@router.get("/pendentes")
def ferias_pendentes(db: Session = Depends(get_db), _=Depends(require_admin)):
    pendentes = (
        db.query(Ferias)
        .filter(Ferias.status == "pendente")
        .order_by(Ferias.criado_em.asc())
        .all()
    )
    return [_fmt_ferias(f) for f in pendentes]


@router.get("/todas")
def todas_ferias(db: Session = Depends(get_db), _=Depends(require_admin)):
    todas = db.query(Ferias).order_by(Ferias.criado_em.desc()).all()
    return [_fmt_ferias(f) for f in todas]


@router.get("/disponibilidade")
def disponibilidade(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todas_ferias = (
        db.query(Ferias)
        .filter(Ferias.status == "aprovada")
        .order_by(Ferias.data_inicio)
        .all()
    )
    user_ids = {f.user_id for f in todas_ferias}
    users_by_id = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    ferias_marcadas = [
        {
            "id": f.id,
            "user_id": f.user_id,
            "nome": users_by_id.get(f.user_id).nome if users_by_id.get(f.user_id) else "Colaborador",
            "data_inicio": f.data_inicio,
            "data_fim": f.data_fim,
            "dias_usados": f.dias_usados,
            "ferias_acordo": f.ferias_acordo,
        }
        for f in todas_ferias
    ]

    if not todas_ferias:
        return {"periodos_bloqueados": [], "ferias_marcadas": []}

    # Determinar limite relevante para o usuário atual
    limite = get_limite_departamento(current_user, db)

    data_min = min(f.data_inicio for f in todas_ferias)
    data_max = max(f.data_fim for f in todas_ferias)

    bloqueados = []
    current_day = data_min
    while current_day <= data_max:
        # Considera apenas férias do mesmo departamento (ou todas) para bloqueio
        if current_user.departamento_id:
            colegas_ids = {
                u.id for u in db.query(User).filter(User.departamento_id == current_user.departamento_id).all()
            }
        else:
            colegas_ids = None

        count = sum(
            1 for f in todas_ferias
            if f.data_inicio <= current_day <= f.data_fim
            and (colegas_ids is None or f.user_id in colegas_ids)
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

    return {"periodos_bloqueados": periodos, "ferias_marcadas": ferias_marcadas}


@router.post("", status_code=status.HTTP_201_CREATED)
def registrar_ferias(
    payload: FeriasCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dias_solicitados = calcular_dias(payload.data_inicio, payload.data_fim)

    # Férias por acordo: não passa pelas regras de saldo/limite, vai direto como pendente
    if not payload.ferias_acordo:
        if verificar_sobreposicao_departamento(db, current_user, payload.data_inicio, payload.data_fim):
            limite = get_limite_departamento(current_user, db)
            raise HTTPException(
                status_code=400,
                detail=f"Limite de {limite} colaborador(es) simultâneo(s) no departamento já atingido no período solicitado.",
            )

        saldo = calcular_saldo(db, current_user)
        if saldo < dias_solicitados:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Você possui {saldo} dia(s) disponível(is) no ciclo atual, mas solicitou {dias_solicitados}.",
            )

    # Admin cria direto como aprovada; usuário comum cria como pendente
    novo_status = "aprovada" if current_user.role == "admin" else "pendente"

    nova_ferias = Ferias(
        user_id=current_user.id,
        data_inicio=payload.data_inicio,
        data_fim=payload.data_fim,
        dias_usados=dias_solicitados,
        status=novo_status,
        ferias_acordo=payload.ferias_acordo,
    )
    db.add(nova_ferias)
    db.flush()

    acao = "FERIAS_REGISTRADA" if novo_status == "aprovada" else "FERIAS_SOLICITADA"
    log = Log(
        user_id=current_user.id,
        acao=acao,
        detalhes=f"Período: {payload.data_inicio} a {payload.data_fim} ({dias_solicitados} dias) — status: {novo_status}",
    )
    db.add(log)
    db.commit()
    db.refresh(nova_ferias)

    return _fmt_ferias(nova_ferias)


@router.put("/{ferias_id}/aprovar")
def aprovar_ferias(
    ferias_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ferias = db.query(Ferias).filter(Ferias.id == ferias_id).first()
    if not ferias:
        raise HTTPException(status_code=404, detail="Férias não encontradas")
    if ferias.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Solicitação não está pendente (status atual: {ferias.status})")

    owner = db.query(User).filter(User.id == ferias.user_id).first()

    if not ferias.ferias_acordo:
        if verificar_sobreposicao_departamento(db, owner, ferias.data_inicio, ferias.data_fim, excluir_ferias_id=ferias_id):
            limite = get_limite_departamento(owner, db)
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível aprovar: limite de {limite} simultâneo(s) no departamento seria excedido.",
            )

    ferias.status = "aprovada"
    ferias.motivo_rejeicao = None

    log = Log(
        user_id=current_user.id,
        acao="FERIAS_APROVADA",
        detalhes=f"Férias #{ferias_id} de {owner.nome} aprovadas ({ferias.data_inicio} a {ferias.data_fim})",
    )
    db.add(log)
    db.commit()
    db.refresh(ferias)

    return _fmt_ferias(ferias)


@router.put("/{ferias_id}/rejeitar")
def rejeitar_ferias(
    ferias_id: int,
    payload: FeriasAprovar,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ferias = db.query(Ferias).filter(Ferias.id == ferias_id).first()
    if not ferias:
        raise HTTPException(status_code=404, detail="Férias não encontradas")
    if ferias.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Solicitação não está pendente (status atual: {ferias.status})")

    owner = db.query(User).filter(User.id == ferias.user_id).first()

    ferias.status = "rejeitada"
    ferias.motivo_rejeicao = payload.motivo_rejeicao

    log = Log(
        user_id=current_user.id,
        acao="FERIAS_REJEITADA",
        detalhes=f"Férias #{ferias_id} de {owner.nome} rejeitadas. Motivo: {payload.motivo_rejeicao or 'não informado'}",
    )
    db.add(log)
    db.commit()
    db.refresh(ferias)

    return _fmt_ferias(ferias)


@router.put("/{ferias_id}")
def editar_ferias(
    ferias_id: int,
    payload: FeriasUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ferias = db.query(Ferias).filter(Ferias.id == ferias_id).first()
    if not ferias:
        raise HTTPException(status_code=404, detail="Férias não encontradas")

    # Usuário comum só edita as próprias, apenas se pendentes
    if current_user.role != "admin":
        if ferias.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Sem permissão para editar férias de outro usuário")
        if ferias.status not in ("pendente",):
            raise HTTPException(status_code=403, detail="Apenas férias pendentes podem ser editadas pelo colaborador")

    owner = db.query(User).filter(User.id == ferias.user_id).first()
    nova_inicio = payload.data_inicio if payload.data_inicio is not None else ferias.data_inicio
    nova_fim = payload.data_fim if payload.data_fim is not None else ferias.data_fim
    dias_solicitados = calcular_dias(nova_inicio, nova_fim)

    novo_acordo = payload.ferias_acordo if payload.ferias_acordo is not None else ferias.ferias_acordo

    if not novo_acordo:
        if verificar_sobreposicao_departamento(db, owner, nova_inicio, nova_fim, excluir_ferias_id=ferias_id):
            limite = get_limite_departamento(owner, db)
            raise HTTPException(
                status_code=400,
                detail=f"Limite de {limite} simultâneo(s) no departamento seria excedido.",
            )

        saldo = calcular_saldo(db, owner, excluir_ferias_id=ferias_id)
        if saldo < dias_solicitados:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Disponível: {saldo} dia(s), solicitado: {dias_solicitados}.",
            )

    ferias.data_inicio = nova_inicio
    ferias.data_fim = nova_fim
    ferias.dias_usados = dias_solicitados
    ferias.ferias_acordo = novo_acordo

    # Apenas admin pode alterar status diretamente
    if current_user.role == "admin":
        if payload.status is not None:
            if payload.status not in ("pendente", "aprovada", "rejeitada"):
                raise HTTPException(status_code=400, detail="Status inválido")
            ferias.status = payload.status
        if payload.motivo_rejeicao is not None:
            ferias.motivo_rejeicao = payload.motivo_rejeicao

    log = Log(
        user_id=current_user.id,
        acao="FERIAS_EDITADA",
        detalhes=f"Férias #{ferias_id} de {owner.nome} alteradas para {nova_inicio} a {nova_fim} ({dias_solicitados} dias)",
    )
    db.add(log)
    db.commit()
    db.refresh(ferias)

    return _fmt_ferias(ferias)


@router.delete("/{ferias_id}", status_code=status.HTTP_200_OK)
def cancelar_ferias(
    ferias_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ferias = db.query(Ferias).filter(Ferias.id == ferias_id).first()
    if not ferias:
        raise HTTPException(status_code=404, detail="Férias não encontradas")

    if current_user.role != "admin" and ferias.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para cancelar férias de outro usuário")

    owner = db.query(User).filter(User.id == ferias.user_id).first()
    detalhes = f"Férias #{ferias_id} de {owner.nome if owner else '?'} ({ferias.data_inicio} a {ferias.data_fim}) canceladas"
    db.delete(ferias)

    log = Log(user_id=current_user.id, acao="FERIAS_CANCELADA", detalhes=detalhes)
    db.add(log)
    db.commit()

    return {"detail": "Férias canceladas com sucesso"}
