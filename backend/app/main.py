import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine, SessionLocal
from app.models import User, Ferias, Log  # importa para registrar no metadata
from app.database import Base
from app.routers import auth, users, ferias, relatorios
from app.core.security import hash_senha

load_dotenv()

app = FastAPI(
    title="Sistema de Gestão de Férias",
    description="API para gerenciamento de férias de colaboradores",
    version="1.0.0",
)

# CORS — permite requisições do Lovable e desenvolvimento local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringir para FRONTEND_URL em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Registrar routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(ferias.router)
app.include_router(relatorios.router)


@app.on_event("startup")
def startup():
    # Criar tabelas automaticamente se não existirem
    Base.metadata.create_all(bind=engine)

    # Criar admin padrão se não houver nenhum usuário admin
    db = SessionLocal()
    try:
        admin_existente = db.query(User).filter(User.role == "admin").first()
        if not admin_existente:
            admin = User(
                nome="Administrador",
                email="admin@sistema.com",
                senha_hash=hash_senha("admin123"),
                role="admin",
                dias_totais=30,
            )
            db.add(admin)
            db.flush()

            log = Log(
                user_id=admin.id,
                acao="USUARIO_CRIADO",
                detalhes="Administrador padrão criado automaticamente",
            )
            db.add(log)
            db.commit()
            print("Admin padrão criado: admin@sistema.com / admin123")
    finally:
        db.close()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "API de Gestão de Férias rodando"}
