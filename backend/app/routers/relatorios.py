from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models.user import User
from app.models.ferias import Ferias
from app.models.log import Log
from app.models.departamento import Departamento
from app.core.security import require_admin

router = APIRouter(tags=["Relatórios e Logs"])


@router.get("/relatorios")
def relatorio_colaboradores(db: Session = Depends(get_db), _=Depends(require_admin)):
    from app.services.ferias_service import calcular_saldo, get_ciclo_atual

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


@router.get("/dashboard")
def dashboard_admin(db: Session = Depends(get_db), _=Depends(require_admin)):
    today = date.today()

    total_colaboradores = db.query(User).filter(User.role == "user").count()
    total_ferias_aprovadas = db.query(Ferias).filter(Ferias.status == "aprovada").count()
    total_ferias_pendentes = db.query(Ferias).filter(Ferias.status == "pendente").count()
    total_ferias_rejeitadas = db.query(Ferias).filter(Ferias.status == "rejeitada").count()
    total_departamentos = db.query(Departamento).count()

    # Férias em andamento hoje
    em_ferias_hoje = db.query(Ferias).filter(
        Ferias.status == "aprovada",
        Ferias.data_inicio <= today,
        Ferias.data_fim >= today,
    ).all()

    pessoas_em_ferias = []
    for f in em_ferias_hoje:
        if f.usuario:
            pessoas_em_ferias.append({
                "id": f.user_id,
                "nome": f.usuario.nome,
                "cor": f.usuario.cor,
                "data_inicio": f.data_inicio,
                "data_fim": f.data_fim,
                "dias_restantes": (f.data_fim - today).days + 1,
            })

    # Próximas férias (próximos 30 dias)
    proximas = db.query(Ferias).filter(
        Ferias.status == "aprovada",
        Ferias.data_inicio > today,
        Ferias.data_inicio <= today + timedelta(days=30),
    ).order_by(Ferias.data_inicio).all()

    proximas_ferias = []
    for f in proximas:
        if f.usuario:
            proximas_ferias.append({
                "id": f.id,
                "nome_usuario": f.usuario.nome,
                "cor": f.usuario.cor,
                "data_inicio": f.data_inicio,
                "data_fim": f.data_fim,
                "dias_usados": f.dias_usados,
            })

    # Alertas de contabilidade (férias nos próximos 4 dias)
    alertas_contabilidade = db.query(Ferias).filter(
        Ferias.status == "aprovada",
        Ferias.data_inicio >= today,
        Ferias.data_inicio <= today + timedelta(days=4),
    ).all()

    alertas = []
    for f in alertas_contabilidade:
        if f.usuario:
            dias_para_inicio = (f.data_inicio - today).days
            alertas.append({
                "ferias_id": f.id,
                "nome_usuario": f.usuario.nome,
                "data_inicio": f.data_inicio,
                "data_fim": f.data_fim,
                "dias_para_inicio": dias_para_inicio,
            })

    return {
        "total_colaboradores": total_colaboradores,
        "total_ferias_aprovadas": total_ferias_aprovadas,
        "total_ferias_pendentes": total_ferias_pendentes,
        "total_ferias_rejeitadas": total_ferias_rejeitadas,
        "total_departamentos": total_departamentos,
        "pessoas_em_ferias": pessoas_em_ferias,
        "proximas_ferias": proximas_ferias,
        "alertas_contabilidade": alertas,
    }


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
