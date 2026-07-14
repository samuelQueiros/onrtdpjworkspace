from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.patrimonio import (
    Equipamento,
    EquipamentoEvento,
    EquipamentoVinculo,
    SolicitacaoEquipamento,
    SolicitacaoEquipamentoEvento,
    SolicitacaoEquipamentoItem,
    TermoEquipamentoVersao,
)
from app.models.user import User


def _carregar_equipamento(query):
    return query.options(
        selectinload(Equipamento.vinculos).joinedload(EquipamentoVinculo.usuario),
        selectinload(Equipamento.vinculos).joinedload(EquipamentoVinculo.vinculado_por),
        selectinload(Equipamento.vinculos).joinedload(EquipamentoVinculo.desvinculado_por),
        selectinload(Equipamento.eventos).joinedload(EquipamentoEvento.criado_por),
    )


def listar_equipamentos(
    db: Session,
    busca: str | None,
    tipo: str | None,
    status: str | None,
    ativo: bool | None,
    user_id: int | None,
    offset: int,
    limit: int,
) -> tuple[list[Equipamento], int]:
    query = db.query(Equipamento)
    if busca or user_id:
        query = query.outerjoin(
            EquipamentoVinculo,
            (EquipamentoVinculo.equipamento_id == Equipamento.id)
            & EquipamentoVinculo.desvinculado_em.is_(None),
        ).outerjoin(User, User.id == EquipamentoVinculo.user_id)
    if busca:
        termo = f"%{busca.strip()}%"
        query = query.filter(
            or_(
                Equipamento.numero_patrimonio.ilike(termo),
                Equipamento.numero_serie.ilike(termo),
                Equipamento.tipo.ilike(termo),
                Equipamento.marca.ilike(termo),
                Equipamento.modelo.ilike(termo),
                User.nome.ilike(termo),
            )
        )
    if tipo:
        query = query.filter(Equipamento.tipo == tipo)
    if status:
        query = query.filter(Equipamento.status == status)
    if ativo is not None:
        query = query.filter(Equipamento.ativo.is_(ativo))
    if user_id:
        query = query.filter(EquipamentoVinculo.user_id == user_id)

    total = query.with_entities(func.count(func.distinct(Equipamento.id))).scalar() or 0
    items = (
        _carregar_equipamento(query)
        .distinct()
        .order_by(Equipamento.ativo.desc(), Equipamento.criado_em.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return items, total


def obter_equipamento(db: Session, equipamento_id: int, bloquear: bool = False) -> Equipamento | None:
    query = db.query(Equipamento).filter(Equipamento.id == equipamento_id)
    if bloquear:
        query = query.with_for_update(of=Equipamento)
    return _carregar_equipamento(query).first()


def obter_equipamentos_por_ids(db: Session, ids: list[int], bloquear: bool = False) -> list[Equipamento]:
    query = db.query(Equipamento).filter(Equipamento.id.in_(ids)).order_by(Equipamento.id)
    if bloquear:
        query = query.with_for_update(of=Equipamento)
    return _carregar_equipamento(query).all()


def obter_por_patrimonio(db: Session, numero: str, excluir_id: int | None = None) -> Equipamento | None:
    query = db.query(Equipamento).filter(func.lower(Equipamento.numero_patrimonio) == numero.lower())
    if excluir_id:
        query = query.filter(Equipamento.id != excluir_id)
    return query.first()


def obter_por_serie(db: Session, numero: str, excluir_id: int | None = None) -> Equipamento | None:
    query = db.query(Equipamento).filter(func.lower(Equipamento.numero_serie) == numero.lower())
    if excluir_id:
        query = query.filter(Equipamento.id != excluir_id)
    return query.first()


def obter_vinculo_ativo(db: Session, equipamento_id: int, bloquear: bool = False) -> EquipamentoVinculo | None:
    query = db.query(EquipamentoVinculo).filter(
        EquipamentoVinculo.equipamento_id == equipamento_id,
        EquipamentoVinculo.desvinculado_em.is_(None),
    )
    if bloquear:
        query = query.with_for_update(of=EquipamentoVinculo)
    return query.options(joinedload(EquipamentoVinculo.usuario)).first()


def listar_vinculos_ativos_usuario(db: Session, user_id: int) -> list[EquipamentoVinculo]:
    return (
        db.query(EquipamentoVinculo)
        .options(joinedload(EquipamentoVinculo.equipamento), joinedload(EquipamentoVinculo.usuario))
        .filter(EquipamentoVinculo.user_id == user_id, EquipamentoVinculo.desvinculado_em.is_(None))
        .order_by(EquipamentoVinculo.vinculado_em)
        .all()
    )


def listar_vinculos_equipamento(db: Session, equipamento_id: int) -> list[EquipamentoVinculo]:
    return (
        db.query(EquipamentoVinculo)
        .options(
            joinedload(EquipamentoVinculo.usuario),
            joinedload(EquipamentoVinculo.vinculado_por),
            joinedload(EquipamentoVinculo.desvinculado_por),
        )
        .filter(EquipamentoVinculo.equipamento_id == equipamento_id)
        .order_by(EquipamentoVinculo.vinculado_em.desc())
        .all()
    )


def listar_disponiveis(db: Session) -> list[Equipamento]:
    return (
        db.query(Equipamento)
        .outerjoin(
            EquipamentoVinculo,
            (EquipamentoVinculo.equipamento_id == Equipamento.id)
            & EquipamentoVinculo.desvinculado_em.is_(None),
        )
        .filter(
            Equipamento.ativo.is_(True),
            Equipamento.status == "disponivel",
            EquipamentoVinculo.id.is_(None),
        )
        .order_by(Equipamento.tipo, Equipamento.marca, Equipamento.modelo)
        .all()
    )


def contar_maquinas_principais_ativas(db: Session, user_id: int, excluir_equipamento_id: int | None = None) -> int:
    query = db.query(EquipamentoVinculo).filter(
        EquipamentoVinculo.user_id == user_id,
        EquipamentoVinculo.desvinculado_em.is_(None),
        EquipamentoVinculo.maquina_principal.is_(True),
    )
    if excluir_equipamento_id:
        query = query.filter(EquipamentoVinculo.equipamento_id != excluir_equipamento_id)
    return query.count()


def obter_usuario_bloqueado(db: Session, user_id: int) -> User | None:
    """Serializa decisoes que alteram os vinculos de um mesmo colaborador."""
    return db.query(User).filter(User.id == user_id).with_for_update(of=User).first()


def obter_solicitacao(db: Session, solicitacao_id: int, bloquear: bool = False) -> SolicitacaoEquipamento | None:
    query = db.query(SolicitacaoEquipamento).filter(SolicitacaoEquipamento.id == solicitacao_id)
    if bloquear:
        query = query.with_for_update(of=SolicitacaoEquipamento)
    return query.options(
        joinedload(SolicitacaoEquipamento.usuario).joinedload(User.cargo),
        joinedload(SolicitacaoEquipamento.usuario).joinedload(User.departamento),
        joinedload(SolicitacaoEquipamento.aprovado_por),
        joinedload(SolicitacaoEquipamento.rejeitado_por),
        joinedload(SolicitacaoEquipamento.entregue_por),
        joinedload(SolicitacaoEquipamento.termo_versao),
        selectinload(SolicitacaoEquipamento.itens).joinedload(SolicitacaoEquipamentoItem.equipamento),
        selectinload(SolicitacaoEquipamento.eventos).joinedload(SolicitacaoEquipamentoEvento.criado_por),
    ).first()


def listar_solicitacoes_usuario(db: Session, user_id: int) -> list[SolicitacaoEquipamento]:
    ids = [
        row[0]
        for row in db.query(SolicitacaoEquipamento.id)
        .filter(SolicitacaoEquipamento.user_id == user_id)
        .order_by(SolicitacaoEquipamento.criado_em.desc())
        .all()
    ]
    return [solicitacao for item_id in ids if (solicitacao := obter_solicitacao(db, item_id))]


def listar_solicitacoes_admin(
    db: Session,
    status: str | None = None,
    user_id: int | None = None,
    equipamento_id: int | None = None,
    criado_de: datetime | None = None,
    criado_ate: datetime | None = None,
) -> list[SolicitacaoEquipamento]:
    # O PostgreSQL exige que toda coluna usada no ORDER BY esteja presente no
    # SELECT quando DISTINCT e aplicado. A data tambem participa do SELECT para
    # manter a deduplicacao dos IDs resultantes do join com os itens.
    query = db.query(SolicitacaoEquipamento.id, SolicitacaoEquipamento.criado_em)
    if equipamento_id:
        query = query.join(SolicitacaoEquipamentoItem).filter(
            SolicitacaoEquipamentoItem.equipamento_id == equipamento_id
        )
    if status:
        query = query.filter(SolicitacaoEquipamento.status == status)
    if user_id:
        query = query.filter(SolicitacaoEquipamento.user_id == user_id)
    if criado_de:
        query = query.filter(SolicitacaoEquipamento.criado_em >= criado_de)
    if criado_ate:
        query = query.filter(SolicitacaoEquipamento.criado_em <= criado_ate)
    ids = [
        row[0]
        for row in query.distinct()
        .order_by(SolicitacaoEquipamento.criado_em.desc(), SolicitacaoEquipamento.id.desc())
        .all()
    ]
    return [solicitacao for item_id in ids if (solicitacao := obter_solicitacao(db, item_id))]


def existe_solicitacao_concorrente(db: Session, user_id: int, equipamento_id: int) -> bool:
    return (
        db.query(SolicitacaoEquipamentoItem.id)
        .join(SolicitacaoEquipamento)
        .filter(
            SolicitacaoEquipamento.user_id == user_id,
            SolicitacaoEquipamento.status.in_(
                [
                    "pendente",
                    "aprovada",
                    "aguardando_entrega",
                    "aguardando_aceite",
                    "aceite_registrado_aguardando_documento",
                    "entregue",
                ]
            ),
            SolicitacaoEquipamentoItem.equipamento_id == equipamento_id,
            SolicitacaoEquipamentoItem.status_item != "removido",
        )
        .first()
        is not None
    )


def existe_autorizacao_entregue_em_aberto(db: Session, equipamento_id: int) -> bool:
    return (
        db.query(SolicitacaoEquipamentoItem.id)
        .join(SolicitacaoEquipamento)
        .filter(
            SolicitacaoEquipamento.status.in_(
                ["aguardando_aceite", "aceite_registrado_aguardando_documento", "entregue"]
            ),
            SolicitacaoEquipamentoItem.equipamento_id == equipamento_id,
            SolicitacaoEquipamentoItem.status_item == "entregue",
        )
        .first()
        is not None
    )


def contar_solicitacoes_pendentes(db: Session) -> int:
    return db.query(SolicitacaoEquipamento).filter(SolicitacaoEquipamento.status == "pendente").count()


def obter_versao_termo_por_codigo(db: Session, codigo: str) -> TermoEquipamentoVersao | None:
    return db.query(TermoEquipamentoVersao).filter(TermoEquipamentoVersao.codigo == codigo).first()


def salvar(db: Session, *objetos) -> None:
    for objeto in objetos:
        db.add(objeto)


def commit(db: Session) -> None:
    db.commit()


def flush(db: Session) -> None:
    db.flush()
