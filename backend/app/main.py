from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import SessionLocal
from app.routers import auth, users, ferias, relatorios
from app.routers import departamentos, avisos, documentos, importacao, bloqueios, alertas, credenciais
from app.services import bootstrap_service

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
