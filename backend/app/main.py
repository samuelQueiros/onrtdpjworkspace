import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models import User, Ferias, Log, Departamento, Aviso, Documento, BloqueioData, Alerta, Credencial, CredencialUsuario
from app.routers import auth, users, ferias, relatorios
from app.routers import departamentos, avisos, documentos, importacao, bloqueios, alertas, credenciais
from app.core.security import hash_senha

load_dotenv()

app = FastAPI(
    title="Gestão RH",
    description="API para gerenciamento de férias e RH de colaboradores",
    version="2.0.0",
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
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
    documentos.inicializar_diretorios_upload()

    db = SessionLocal()
    try:
        admin_existente = db.query(User).filter(User.role == "admin").first()
        if not admin_existente:
            admin_email = os.getenv("ADMIN_EMAIL")
            admin_password = os.getenv("ADMIN_PASSWORD")
            admin_name = os.getenv("ADMIN_NAME", "Administrador")

            if admin_email and admin_password:
                admin = User(
                    nome=admin_name,
                    email=admin_email,
                    senha_hash=hash_senha(admin_password),
                    role="admin",
                    dias_totais=30,
                )
                db.add(admin)
                db.flush()

                log = Log(user_id = admin.id, acao = "USUARIO_CRIADO", detalhes = "Administrador inicial criado automaticamente.")
                db.add(log)
                db.commit()
                print(f"Admin inicial criado: {admin_email}")
            else:
                print("Nenhum administrador encontrado. Configure ADMIN_EMAIL e ADMIN_PASSWORD.")
    finally:
        db.close()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "API de Gestão RH — v2.0"}
