from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ferias import Ferias
from app.models.log import Log
from app.core.security import require_admin

router = APIRouter(tags=["Relatórios e Logs"])


@router.get("/relatorios")
def relatorio_colaboradores(db: Session = Depends(get_db), _=Depends(require_admin)):
    from app.routers.ferias import calcular_saldo, get_ciclo_atual

    users = db.query(User).order_by(User.nome).all()
    colaboradores = []

    for user in users:
        ciclo_inicio, ciclo_fim = get_ciclo_atual(user.data_admissao)

        ferias_ciclo = db.query(Ferias).filter(
            Ferias.user_id == user.id,
            Ferias.ferias_acordo == False,  # noqa: E712
            Ferias.status == "aprovada",
            Ferias.data_inicio >= ciclo_inicio,
        ).all()

        ferias_acordo = db.query(Ferias).filter(
            Ferias.user_id == user.id,
            Ferias.ferias_acordo == True,  # noqa: E712
            Ferias.status == "aprovada",
        ).all()

        ferias_pendentes = db.query(Ferias).filter(
            Ferias.user_id == user.id,
            Ferias.status == "pendente",
        ).all()

        dias_usados = sum(f.dias_usados for f in ferias_ciclo)

        dep = None
        if user.departamento_id and user.departamento:
            dep = {"id": user.departamento.id, "nome": user.departamento.nome}

        colaboradores.append({
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "departamento": dep,
            "dias_totais": user.dias_totais,
            "dias_usados": dias_usados,
            "dias_restantes": user.dias_totais - dias_usados,
            "ciclo_inicio": ciclo_inicio,
            "ciclo_fim": ciclo_fim,
            "ferias": [
                {
                    "id": f.id,
                    "data_inicio": f.data_inicio,
                    "data_fim": f.data_fim,
                    "dias_usados": f.dias_usados,
                    "status": f.status,
                    "ferias_acordo": f.ferias_acordo,
                }
                for f in ferias_ciclo
            ],
            "ferias_acordo": [
                {
                    "id": f.id,
                    "data_inicio": f.data_inicio,
                    "data_fim": f.data_fim,
                    "dias_usados": f.dias_usados,
                }
                for f in ferias_acordo
            ],
            "ferias_pendentes": [
                {
                    "id": f.id,
                    "data_inicio": f.data_inicio,
                    "data_fim": f.data_fim,
                    "dias_usados": f.dias_usados,
                }
                for f in ferias_pendentes
            ],
        })

    return {"colaboradores": colaboradores}


@router.get("/logs")
def listar_logs(db: Session = Depends(get_db), _=Depends(require_admin)):
    logs = db.query(Log).order_by(Log.criado_em.desc()).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "nome_usuario": log.usuario.nome if log.usuario else "Sistema",
            "email_usuario": log.usuario.email if log.usuario else None,
            "acao": log.acao,
            "detalhes": log.detalhes,
            "criado_em": log.criado_em,
        }
        for log in logs
    ]
