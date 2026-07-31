from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine_options = {"pool_pre_ping": True}
if SQLALCHEMY_DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
    engine_options.update(
        {
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "pool_timeout": settings.database_pool_timeout_seconds,
            "pool_recycle": settings.database_pool_recycle_seconds,
            "connect_args": {
                "connect_timeout": settings.database_connect_timeout_seconds,
                "options": f"-c statement_timeout={settings.database_statement_timeout_ms}",
            },
        }
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
