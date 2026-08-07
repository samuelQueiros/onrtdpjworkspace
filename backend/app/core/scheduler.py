"""Agendador em processo (APScheduler) para o job de monitoramento de e-mails de ferias.

Roda dentro do mesmo processo do Uvicorn - adequado ao volume baixo do projeto (no maximo
5 envios/mes). `max_instances=1` evita sobreposicao de ciclos dentro do mesmo processo; a
protecao contra multiplos workers/processos fica a cargo do lock consultivo do Postgres
tomado em `envios_monitoramento_service.executar_ciclo_monitoramento`.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.database import SessionLocal
from app.services import envios_monitoramento_service

logger = logging.getLogger("app.scheduler")


def _executar_ciclo_com_sessao() -> None:
    db = SessionLocal()
    try:
        envios_monitoramento_service.executar_ciclo_monitoramento(db)
    except Exception:
        logger.exception("falha nao tratada no ciclo de monitoramento de envios")
    finally:
        db.close()


def iniciar_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(job_defaults={"max_instances": 1, "misfire_grace_time": 60})
    scheduler.add_job(
        _executar_ciclo_com_sessao,
        "interval",
        minutes=settings.envios_monitoramento_intervalo_minutos,
        id="monitoramento_envios_ferias",
    )
    scheduler.start()
    return scheduler


def parar_scheduler(scheduler: BackgroundScheduler | None) -> None:
    if scheduler is not None:
        scheduler.shutdown(wait=False)
