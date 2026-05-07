import os
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine, SessionLocal
from app.models import User, Ferias, Log, Departamento, Aviso, Documento
from app.database import Base
from app.routers import auth, users, ferias, relatorios
from app.routers import departamentos, avisos, documentos, importacao
from app.core.security import hash_senha

load_dotenv()

app = FastAPI(
    title="Sistema de Gestão de Férias",
    description="API para gerenciamento de férias e RH de colaboradores",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


def _run_migrations():
    """Adiciona colunas novas em tabelas existentes sem recriar o banco."""
    db_path = os.getenv("DATABASE_PATH", "./ferias.db")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        alteracoes = [
            # tabela, coluna, definição
            ("ferias", "status", "TEXT DEFAULT 'aprovada'"),
            ("ferias", "ferias_acordo", "INTEGER DEFAULT 0"),
            ("ferias", "motivo_rejeicao", "TEXT"),
            ("users", "departamento_id", "INTEGER"),
            ("users", "data_admissao", "DATE"),
        ]

        for tabela, coluna, definicao in alteracoes:
            try:
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
            except sqlite3.OperationalError:
                pass  # coluna já existe

        conn.commit()
        conn.close()
    except Exception as exc:
        print(f"[migrations] Aviso: {exc}")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    _run_migrations()

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
    return {"status": "ok", "message": "API de Gestão de Férias e RH — v2.0"}
