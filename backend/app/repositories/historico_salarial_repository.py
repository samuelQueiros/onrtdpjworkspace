from sqlalchemy.orm import Session

from app.models.historico_salarial import HistoricoSalarial


def listar_por_usuario(db: Session, user_id: int) -> list[HistoricoSalarial]:
    return (
        db.query(HistoricoSalarial)
        .filter(HistoricoSalarial.user_id == user_id)
        .order_by(HistoricoSalarial.data_vigencia, HistoricoSalarial.criado_em)
        .all()
    )
