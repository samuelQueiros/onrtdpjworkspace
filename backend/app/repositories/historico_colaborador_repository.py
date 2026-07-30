from sqlalchemy.orm import Session

from app.models.historico_colaborador import HistoricoColaborador


def listar_por_usuario(db: Session, user_id: int) -> list[HistoricoColaborador]:
    return (
        db.query(HistoricoColaborador)
        .filter(HistoricoColaborador.user_id == user_id)
        .order_by(HistoricoColaborador.data_vigencia, HistoricoColaborador.criado_em)
        .all()
    )
