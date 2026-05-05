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
    users = db.query(User).all()
    colaboradores = []

    for user in users:
        ferias_list = db.query(Ferias).filter(Ferias.user_id == user.id).all()
        dias_usados = sum(f.dias_usados for f in ferias_list)

        colaboradores.append({
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "dias_totais": user.dias_totais,
            "dias_usados": dias_usados,
            "dias_restantes": user.dias_totais - dias_usados,
            "ferias": [
                {
                    "id": f.id,
                    "data_inicio": f.data_inicio,
                    "data_fim": f.data_fim,
                    "dias_usados": f.dias_usados,
                }
                for f in ferias_list
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
            "acao": log.acao,
            "detalhes": log.detalhes,
            "criado_em": log.criado_em,
        }
        for log in logs
    ]
