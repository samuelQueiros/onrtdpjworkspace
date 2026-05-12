from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models.alerta import Alerta
from app.models.ferias import Ferias
from app.models.user import User
from app.core.security import require_admin

router = APIRouter(prefix="/alertas", tags=["Alertas"])


def _fmt(a: Alerta) -> dict:
    ferias = a.ferias
    return {
        "id": a.id,
        "ferias_id": a.ferias_id,
        "tipo": a.tipo,
        "mensagem": a.mensagem,
        "lido": a.lido,
        "criado_em": a.criado_em,
        "ferias_data_inicio": ferias.data_inicio if ferias else None,
        "ferias_data_fim": ferias.data_fim if ferias else None,
        "ferias_usuario": ferias.usuario.nome if ferias and ferias.usuario else None,
    }


def gerar_alertas_contabilidade(db: Session):
    """Gera alertas para férias que começam em 4 dias."""
    alvo = date.today() + timedelta(days=4)

    ferias_proximas = (
        db.query(Ferias)
        .filter(Ferias.data_inicio == alvo, Ferias.status == "aprovada")
        .all()
    )

    for f in ferias_proximas:
        ja_existe = db.query(Alerta).filter(
            Alerta.ferias_id == f.id,
            Alerta.tipo == "contabilidade_4dias",
        ).first()
        if not ja_existe:
            usuario_nome = f.usuario.nome if f.usuario else "Colaborador"
            alerta = Alerta(
                ferias_id=f.id,
                tipo="contabilidade_4dias",
                mensagem=(
                    f"Encaminhar documentação à contabilidade: {usuario_nome} "
                    f"entra em férias em {alvo.strftime('%d/%m/%Y')} "
                    f"({f.data_inicio.strftime('%d/%m/%Y')} a {f.data_fim.strftime('%d/%m/%Y')})."
                ),
            )
            db.add(alerta)

    db.commit()


@router.get("")
def listar_alertas(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    gerar_alertas_contabilidade(db)
    alertas = (
        db.query(Alerta)
        .order_by(Alerta.lido.asc(), Alerta.criado_em.desc())
        .all()
    )
    return [_fmt(a) for a in alertas]


@router.put("/{alerta_id}/lido")
def marcar_lido(
    alerta_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if alerta:
        alerta.lido = True
        db.commit()
    return {"detail": "Alerta marcado como lido"}


@router.put("/marcar-todos-lidos")
def marcar_todos_lidos(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    db.query(Alerta).filter(Alerta.lido == False).update({"lido": True})  # noqa: E712
    db.commit()
    return {"detail": "Todos os alertas marcados como lidos"}
