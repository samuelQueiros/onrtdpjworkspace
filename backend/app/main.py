from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from uuid import uuid4
import logging
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
    credenciais,
    departamentos,
    documentos,
    importacao,
    patrimonios,
)
from app.services import bootstrap_service

logger = logging.getLogger("app.http")

app = FastAPI(
    title="Gestão RH",
    description="API para gerenciamento de férias e RH de colaboradores",
    version="2.0.0",
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
    response = await call_next(request)
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
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
app.include_router(importacao.router)
app.include_router(bloqueios.router)
app.include_router(alertas.router)
app.include_router(credenciais.router)
app.include_router(cargos.router)
app.include_router(patrimonios.router)
app.include_router(autorizacoes_equipamentos.router)
app.include_router(autorizacoes_equipamentos.pendencias_router)


@app.on_event("startup")
def startup():
    bootstrap_service.inicializar_uploads()

    db = SessionLocal()
    try:
        resultado = bootstrap_service.garantir_admin_inicial(db)
        if resultado == "admin_criado":
            print(f"Admin inicial criado: {settings.admin_email}")
        elif resultado == "admin_nao_configurado":
            print("Nenhum administrador encontrado. Configure ADMIN_EMAIL e ADMIN_PASSWORD.")
    finally:
        db.close()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "API de Gestão RH — v2.0"}
