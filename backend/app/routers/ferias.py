from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, timedelta
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.ferias import Ferias
from app.models.log import Log
from app.schemas.ferias import FeriasCreate, FeriasUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/ferias", tags=["Férias"])

LIMITE_SIMULTANEO = 2  # máximo de colaboradores em férias ao mesmo tempo


def calcular_dias(data_inicio: date, data_fim: date) -> int:
    # Contagem inclusiva: início e fim contam como dias de férias
    return (data_fim - data_inicio).days + 1


def verificar_sobreposicao(db: Session, data_inicio: date, data_fim: date, excluir_ferias_id: int = None, excluir_user_id: int = None):
    """
    Regra de negócio 1: máximo de LIMITE_SIMULTANEO colaboradores em férias simultaneamente.
    Busca registros de outros usuários cujo período se sobreponha ao solicitado.
    Dois períodos se sobrepõem quando: início_A <= fim_B AND fim_A >= início_B
    """
    query = db.query(Ferias).filter(
        Ferias.data_inicio <= data_fim,
        Ferias.data_fim >= data_inicio,
    )

    if excluir_ferias_id:
        query = query.filter(Ferias.id != excluir_ferias_id)

    if excluir_user_id:
        query = query.filter(Ferias.user_id != excluir_user_id)

    conflitos = query.all()

    # Encontrar o pico de sobreposição dia a dia seria custoso; usamos a abordagem
    # conservadora: se há LIMITE_SIMULTANEO ou mais registros que se sobrepõem ao período,
    # verificamos se algum subperíodo viola o limite (checagem por dia único mais simples
    # de entender e segura para calendários pequenos).
    if len(conflitos) >= LIMITE_SIMULTANEO:
        # Verificação mais precisa: há algum dia dentro do período solicitado
        # onde LIMITE_SIMULTANEO ou mais outros colaboradores estão em férias?
        current = data_inicio
        while current <= data_fim:
            count = sum(
                1 for f in conflitos
                if f.data_inicio <= current <= f.data_fim
            )
            if count >= LIMITE_SIMULTANEO:
                return True
            current += timedelta(days=1)

    return False


def verificar_saldo(db: Session, user: User, dias_solicitados: int, excluir_ferias_id: int = None) -> int:
    """
    Regra de negócio 2: usuário deve ter saldo suficiente de dias.
    Retorna os dias restantes após descontar os já usados.
    """
    query = db.query(Ferias).filter(Ferias.user_id == user.id)
    if excluir_ferias_id:
        query = query.filter(Ferias.id != excluir_ferias_id)

    total_usado = sum(f.dias_usados for f in query.all())
    return user.dias_totais - total_usado


@router.get("/me")
def minhas_ferias(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ferias = db.query(Ferias).filter(Ferias.user_id == current_user.id).all()
    return [
        {
            "id": f.id,
            "user_id": f.user_id,
            "data_inicio": f.data_inicio,
            "data_fim": f.data_fim,
            "dias_usados": f.dias_usados,
            "criado_em": f.criado_em,
        }
        for f in ferias
    ]


@router.get("/disponibilidade")
def disponibilidade(db: Session = Depends(get_db), _=Depends(get_current_user)):
    todas_ferias = db.query(Ferias).order_by(Ferias.data_inicio).all()
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
        }
        for f in todas_ferias
    ]

    if not todas_ferias:
        return {"periodos_bloqueados": [], "ferias_marcadas": []}

    # Encontrar o range completo de datas
    data_min = min(f.data_inicio for f in todas_ferias)
    data_max = max(f.data_fim for f in todas_ferias)

    # Percorrer dia a dia e identificar dias bloqueados
    bloqueados = []
    current = data_min
    while current <= data_max:
        count = sum(1 for f in todas_ferias if f.data_inicio <= current <= f.data_fim)
        if count >= LIMITE_SIMULTANEO:
            bloqueados.append(current)
        current += timedelta(days=1)

    # Agrupar dias consecutivos em períodos
    periodos = []
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

    # Regra 1: verificar limite de colaboradores simultâneos
    if verificar_sobreposicao(db, payload.data_inicio, payload.data_fim, excluir_user_id=current_user.id):
        raise HTTPException(
            status_code=400,
            detail=f"Já existem {LIMITE_SIMULTANEO} colaboradores em férias no período solicitado. Escolha outras datas.",
        )

    # Regra 2: verificar saldo disponível
    saldo = verificar_saldo(db, current_user, dias_solicitados)
    if saldo < dias_solicitados:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Você possui {saldo} dia(s) disponível(is), mas solicitou {dias_solicitados}.",
        )

    # Regra 3: calcular dias_usados automaticamente
    nova_ferias = Ferias(
        user_id=current_user.id,
        data_inicio=payload.data_inicio,
        data_fim=payload.data_fim,
        dias_usados=dias_solicitados,
    )
    db.add(nova_ferias)
    db.flush()

    log = Log(
        user_id=current_user.id,
        acao="FERIAS_REGISTRADA",
        detalhes=f"Período: {payload.data_inicio} a {payload.data_fim} ({dias_solicitados} dias)",
    )
    db.add(log)
    db.commit()
    db.refresh(nova_ferias)

    return {
        "id": nova_ferias.id,
        "user_id": nova_ferias.user_id,
        "data_inicio": nova_ferias.data_inicio,
        "data_fim": nova_ferias.data_fim,
        "dias_usados": nova_ferias.dias_usados,
        "criado_em": nova_ferias.criado_em,
    }


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

    # Usuário comum só pode editar as próprias férias
    if current_user.role != "admin" and ferias.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para editar férias de outro usuário")

    nova_inicio = payload.data_inicio or ferias.data_inicio
    nova_fim = payload.data_fim or ferias.data_fim
    dias_solicitados = calcular_dias(nova_inicio, nova_fim)

    owner = db.query(User).filter(User.id == ferias.user_id).first()

    # Regra 1: verificar conflito com outros usuários (excluindo este registro)
    if verificar_sobreposicao(db, nova_inicio, nova_fim, excluir_ferias_id=ferias_id, excluir_user_id=ferias.user_id):
        raise HTTPException(
            status_code=400,
            detail=f"Já existem {LIMITE_SIMULTANEO} colaboradores em férias no período solicitado. Escolha outras datas.",
        )

    # Regra 2: verificar saldo (excluindo os dias deste registro)
    saldo = verificar_saldo(db, owner, dias_solicitados, excluir_ferias_id=ferias_id)
    if saldo < dias_solicitados:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Disponível: {saldo} dia(s), solicitado: {dias_solicitados}.",
        )

    ferias.data_inicio = nova_inicio
    ferias.data_fim = nova_fim
    ferias.dias_usados = dias_solicitados

    log = Log(
        user_id=current_user.id,
        acao="FERIAS_EDITADA",
        detalhes=f"Férias #{ferias_id} alteradas para {nova_inicio} a {nova_fim} ({dias_solicitados} dias)",
    )
    db.add(log)
    db.commit()
    db.refresh(ferias)

    return {
        "id": ferias.id,
        "user_id": ferias.user_id,
        "data_inicio": ferias.data_inicio,
        "data_fim": ferias.data_fim,
        "dias_usados": ferias.dias_usados,
        "criado_em": ferias.criado_em,
    }


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

    detalhes = f"Férias #{ferias_id} de {ferias.data_inicio} a {ferias.data_fim} canceladas"
    db.delete(ferias)

    log = Log(user_id=current_user.id, acao="FERIAS_CANCELADA", detalhes=detalhes)
    db.add(log)
    db.commit()

    return {"detail": "Férias canceladas com sucesso"}
