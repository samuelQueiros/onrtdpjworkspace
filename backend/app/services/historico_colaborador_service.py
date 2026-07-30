from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.crypto import criptografar_dado_sensivel, descriptografar_dado_sensivel
from app.models.historico_colaborador import HistoricoColaborador
from app.models.user import User
from app.repositories import historico_colaborador_repository


def registrar_alteracao(
    db: Session,
    user_id: int,
    campo: str,
    valor_anterior: str | None,
    valor_novo: str,
    tipo_alteracao: str,
    motivo: str | None,
    current_user: User,
) -> None:
    db.add(HistoricoColaborador(
        user_id=user_id,
        campo=campo,
        valor_anterior_criptografado=(
            criptografar_dado_sensivel(valor_anterior) if valor_anterior is not None else None
        ),
        valor_novo_criptografado=criptografar_dado_sensivel(valor_novo),
        tipo_alteracao=tipo_alteracao,
        motivo=motivo,
        data_vigencia=date.today(),
        criado_por_id=current_user.id,
    ))


def processar_alteracao_se_necessario(
    db: Session,
    user_id: int,
    campo: str,
    valor_anterior: str | None,
    valor_novo: str | None,
    motivo_informado: str | None,
    tipo_informado: str | None,
    current_user: User,
    eh_importacao: bool = False,
) -> None:
    """Compara valor antigo/novo e, se mudou, grava uma linha no historico.

    Primeira atribuicao (valor_anterior None) e importacao em massa nunca
    exigem motivo/tipo do usuario (viram "Cadastro inicial"/"Importacao de
    planilha" automaticamente). Qualquer outra mudanca exige os dois, senao
    levanta 400.
    """
    if valor_novo is None or valor_novo == valor_anterior:
        return

    if valor_anterior is not None and not eh_importacao and not (motivo_informado and tipo_informado):
        raise HTTPException(
            status_code=400,
            detail="Informe o motivo e o tipo (mudança real ou correção) da alteração.",
        )

    if eh_importacao:
        tipo, motivo = "real", "Importação de planilha"
    elif valor_anterior is None:
        tipo, motivo = "real", "Cadastro inicial"
    else:
        tipo, motivo = tipo_informado, motivo_informado

    registrar_alteracao(db, user_id, campo, valor_anterior, valor_novo, tipo, motivo, current_user)


def listar_historico(db: Session, user_id: int) -> list[dict]:
    movimentos = historico_colaborador_repository.listar_por_usuario(db, user_id)
    return [
        {
            "campo": movimento.campo,
            "valor_anterior": (
                descriptografar_dado_sensivel(movimento.valor_anterior_criptografado)
                if movimento.valor_anterior_criptografado else None
            ),
            "valor_novo": descriptografar_dado_sensivel(movimento.valor_novo_criptografado),
            "tipo_alteracao": movimento.tipo_alteracao,
            "motivo": movimento.motivo,
            "data_vigencia": movimento.data_vigencia,
            "criado_em": movimento.criado_em,
        }
        for movimento in movimentos
    ]
