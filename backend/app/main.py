from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from uuid import uuid4
import logging
import os
import time

from app.core.config import settings
from app.database import SessionLocal
from app.routers import auth, users, ferias, relatorios
from app.routers import (
    alertas,
    autorizacoes_equipamentos,
    avisos,
    bloqueios,
    cargos,
    configuracao,
    credenciais,
    departamentos,
    documentos,
    envios,
    fichas_admissionais,
    importacao,
    patrimonios,
    track,
)
from app.core.scheduler import iniciar_scheduler, parar_scheduler
from app.services import bootstrap_service

logger = logging.getLogger("app.http")

app = FastAPI(
    title="Gestão RH",
    description="API para gerenciamento de férias e RH de colaboradores",
    version="2.0.0",
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None if settings.environment == "production" else "/redoc",
    openapi_url=None if settings.environment == "production" else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def security_and_request_id(request: Request, call_next):
    # Identificador autoritativo do servidor; nao reutilize um valor controlado
    # pelo cliente como evidencia do aceite.
    request_id = uuid4().hex
    request.state.request_id = request_id
    inicio = time.perf_counter()
    origin = request.headers.get("origin")
    origem_invalida = (
        request.method not in {"GET", "HEAD", "OPTIONS"}
        and origin is not None
        and origin != settings.frontend_url.rstrip("/")
    )
    if origem_invalida:
        response = JSONResponse(
            status_code=403,
            content={"detail": "Origem da requisicao nao autorizada", "request_id": request_id},
        )
    else:
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "unhandled_exception method=%s path=%s request_id=%s",
                request.method,
                request.url.path,
                request_id,
            )
            response = JSONResponse(
                status_code=500,
                content={"detail": "Erro interno do servidor", "request_id": request_id},
            )
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    if settings.environment == "production" and settings.cookie_secure:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%s request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duracao_ms,
        request_id,
    )
    return response

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(ferias.router)
app.include_router(relatorios.router)
app.include_router(departamentos.router)
app.include_router(avisos.router)
app.include_router(documentos.router)
app.include_router(fichas_admissionais.router)
app.include_router(importacao.router)
app.include_router(bloqueios.router)
app.include_router(alertas.router)
app.include_router(credenciais.router)
app.include_router(cargos.router)
app.include_router(patrimonios.router)
app.include_router(autorizacoes_equipamentos.router)
app.include_router(autorizacoes_equipamentos.pendencias_router)
app.include_router(configuracao.router)
app.include_router(envios.router)
app.include_router(track.router)


@app.on_event("startup")
def startup():
    settings.validate_runtime()
    bootstrap_service.inicializar_uploads()

    db = SessionLocal()
    try:
        resultado = bootstrap_service.garantir_admin_inicial(db)
        if resultado == "admin_criado":
            print(f"Admin inicial criado: {settings.admin_email}")
        elif resultado == "admin_senha_sincronizada":
            print(f"Senha do admin sincronizada a partir de ADMIN_PASSWORD: {settings.admin_email}")
        elif resultado == "admin_email_pertence_a_usuario_nao_admin":
            print(
                f"ADMIN_EMAIL ({settings.admin_email}) pertence a um usuario que nao e administrador. "
                "Nenhuma alteracao foi feita."
            )
        elif resultado == "admin_nao_configurado":
            print("Nenhum administrador encontrado. Configure ADMIN_EMAIL e ADMIN_PASSWORD.")
    finally:
        db.close()

    app.state.scheduler = iniciar_scheduler()


@app.on_event("shutdown")
def shutdown():
    parar_scheduler(getattr(app.state, "scheduler", None))


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "API de Gestão RH — v2.0"}


@app.get("/health/live", tags=["Health"])
def liveness():
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
def readiness():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        upload_dir = settings.upload_dir
        upload_dir.mkdir(parents=True, exist_ok=True)
        if not upload_dir.is_dir() or not os.access(upload_dir, os.W_OK):
            raise RuntimeError("diretório de uploads sem permissão de escrita")
    except Exception as exc:
        logger.error("readiness failed: %s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="Serviço temporariamente indisponível") from exc
    finally:
        db.close()
    return {"status": "ready"}
