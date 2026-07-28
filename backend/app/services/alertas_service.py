from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.repositories import alertas_repository

TIPO_CONTABILIDADE_4_DIAS = "contabilidade_4dias"
TIPO_FERIAS_5_DIAS = "ferias_5dias"
TIPO_FERIAS_4_DIAS = "ferias_4dias"


def formatar_alerta(alerta: Alerta, db: Session | None = None) -> dict:
    from app.services.ferias_service import get_ciclo_atual

    ferias = alerta.ferias
    ciclo_inicio = ciclo_fim = retorno_trabalho = cargo_usuario = None

    if ferias:
        ciclo_inicio, ciclo_fim = get_ciclo_atual(ferias.usuario.data_admissao if ferias.usuario else None)
        retorno_trabalho = ferias.data_fim + timedelta(days=1)
        if ferias.usuario and ferias.usuario.cargo:
            cargo_usuario = ferias.usuario.cargo.nome

    return {
        "id": alerta.id,
        "ferias_id": alerta.ferias_id,
        "tipo": alerta.tipo,
        "mensagem": alerta.mensagem,
        "lido": alerta.lido,
        "criado_em": alerta.criado_em,
        "ferias_data_inicio": ferias.data_inicio if ferias else None,
        "ferias_data_fim": ferias.data_fim if ferias else None,
        "ferias_usuario": ferias.usuario.nome if ferias and ferias.usuario else None,
        "ferias_dias_usados": ferias.dias_usados if ferias else None,
        "cargo_usuario": cargo_usuario,
        "ciclo_inicio": ciclo_inicio,
        "ciclo_fim": ciclo_fim,
        "retorno_trabalho": retorno_trabalho,
    }


def gerar_alertas_contabilidade(db: Session, hoje: date | None = None) -> None:
    alvo = (hoje or date.today()) + timedelta(days=6)
    ferias_proximas = alertas_repository.listar_ferias_aprovadas_por_data_inicio(db, alvo)

    for ferias in ferias_proximas:
        if alertas_repository.existe_alerta_por_ferias_e_tipo(db, ferias.id, TIPO_CONTABILIDADE_4_DIAS):
            continue

        usuario_nome = ferias.usuario.nome if ferias.usuario else "Colaborador"
        alerta = Alerta(
            ferias_id=ferias.id,
            tipo=TIPO_CONTABILIDADE_4_DIAS,
            mensagem=(
                f"Encaminhar documentacao a contabilidade: {usuario_nome} "
                f"entra em ferias em {alvo.strftime('%d/%m/%Y')} "
                f"({ferias.data_inicio.strftime('%d/%m/%Y')} a {ferias.data_fim.strftime('%d/%m/%Y')})."
            ),
        )
        alertas_repository.adicionar_alerta(db, alerta)

    alertas_repository.salvar_alertas(db)


def gerar_alertas_ferias_5dias(db: Session, hoje: date | None = None) -> None:
    alvo = (hoje or date.today()) + timedelta(days=7)

    ferias_proximas = alertas_repository.listar_ferias_aprovadas_por_data_inicio(db, alvo)

    for ferias in ferias_proximas:
        if alertas_repository.existe_alerta_por_ferias_e_tipo(db, ferias.id, TIPO_FERIAS_5_DIAS):
            continue

        usuario_nome = ferias.usuario.nome if ferias.usuario else "Colaborador"
        alerta = Alerta(
            ferias_id=ferias.id,
            tipo=TIPO_FERIAS_5_DIAS,
            mensagem=(
                f"{usuario_nome} entra em ferias em {alvo.strftime('%d/%m/%Y')} "
                f"({ferias.data_inicio.strftime('%d/%m/%Y')} a {ferias.data_fim.strftime('%d/%m/%Y')})."
            ),
        )
        alertas_repository.adicionar_alerta(db, alerta)

    alertas_repository.salvar_alertas(db)


def gerar_alertas_ferias_4dias(db: Session, hoje: date | None = None) -> None:
    """Lembrete urgente do dia anterior ao limite de 5 dias: reaparece a cada
    login do admin (o frontend nao considera o campo `lido` para este tipo)."""
    alvo = (hoje or date.today()) + timedelta(days=6)
    ferias_proximas = alertas_repository.listar_ferias_aprovadas_por_data_inicio(db, alvo)

    for ferias in ferias_proximas:
        if alertas_repository.existe_alerta_por_ferias_e_tipo(db, ferias.id, TIPO_FERIAS_4_DIAS):
            continue

        usuario_nome = ferias.usuario.nome if ferias.usuario else "Colaborador"
        alerta = Alerta(
            ferias_id=ferias.id,
            tipo=TIPO_FERIAS_4_DIAS,
            mensagem=(
                f"Lembrete: {usuario_nome} entra em ferias em {alvo.strftime('%d/%m/%Y')} "
                f"({ferias.data_inicio.strftime('%d/%m/%Y')} a {ferias.data_fim.strftime('%d/%m/%Y')})."
            ),
        )
        alertas_repository.adicionar_alerta(db, alerta)

    alertas_repository.salvar_alertas(db)


def listar_alertas(db: Session) -> list[dict]:
    gerar_alertas_contabilidade(db)
    gerar_alertas_ferias_5dias(db)
    gerar_alertas_ferias_4dias(db)
    return [formatar_alerta(alerta, db) for alerta in alertas_repository.listar_alertas(db)]


def marcar_lido(db: Session, alerta_id: int) -> None:
    alerta = alertas_repository.obter_alerta_por_id(db, alerta_id)
    if alerta:
        alertas_repository.marcar_alerta_lido(db, alerta)


def marcar_todos_lidos(db: Session) -> None:
    alertas_repository.marcar_todos_lidos(db)
