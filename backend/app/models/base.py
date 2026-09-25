"""
Configuração central do SQLAlchemy: engine, sessão e Base declarativa.
Compartilhado por todos os módulos (auth, questions, interview).
"""
import os
from dotenv import load_dotenv 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não configurada. Copie backend/.env.example para backend/.env."
    )
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c lc_messages=C"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI para injetar uma sessão de banco por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
