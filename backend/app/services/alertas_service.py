from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.repositories import alertas_repository

TIPO_CONTABILIDADE_4_DIAS = "contabilidade_4dias"


def formatar_alerta(alerta: Alerta) -> dict:
    ferias = alerta.ferias
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
    }


def gerar_alertas_contabilidade(db: Session, hoje: date | None = None) -> None:
    alvo = (hoje or date.today()) + timedelta(days=4)
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


def listar_alertas(db: Session) -> list[dict]:
    gerar_alertas_contabilidade(db)
    return [formatar_alerta(alerta) for alerta in alertas_repository.listar_alertas(db)]


def marcar_lido(db: Session, alerta_id: int) -> None:
    alerta = alertas_repository.obter_alerta_por_id(db, alerta_id)
    if alerta:
        alertas_repository.marcar_alerta_lido(db, alerta)


def marcar_todos_lidos(db: Session) -> None:
    alertas_repository.marcar_todos_lidos(db)
