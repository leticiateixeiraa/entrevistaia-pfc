"""
Entrypoint da API. Cada integrante registra o próprio router aqui
(um `include_router` por módulo) — evita conflito de merge nos outros arquivos.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.base import Base, engine
from app.auth.router import router as auth_router

# from app.questions.router import router as questions_router   # Leonardo: descomentar quando existir
# from app.interview.router import router as interview_router   # Gabriel: descomentar quando existir

app = FastAPI(title="EntrevistaIA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL do Vite em dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
# app.include_router(questions_router)
# app.include_router(interview_router)


@app.on_event("startup")
def on_startup():
    # Cria as tabelas que ainda não existirem (uso simples em dev;
    # em produção prefira Alembic para migrações versionadas).
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}
