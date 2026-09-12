import uuid

from sqlalchemy.orm import Session

from app.interview import service as interview_service
from app.interview.models import InterviewSession


CATEGORIES = [
    {
        "id": "entrevista_de_emprego",
        "name": "Entrevista de emprego",
        "description": "Pratique respostas para processos seletivos e primeiras conversas com recrutadores.",
    },
    {
        "id": "apresentacao_academica",
        "name": "Apresentação acadêmica",
        "description": "Organize e apresente seu trabalho com clareza, segurança e objetividade.",
    },
]


def list_categories() -> list[dict[str, str]]:
    return CATEGORIES


def start_interview(db: Session, user_id: uuid.UUID, category: str) -> InterviewSession:
    valid_ids = {item["id"] for item in CATEGORIES}
    if category not in valid_ids:
        raise ValueError("Categoria de entrevista inválida")
    return interview_service.start_mock_session(db, user_id, category)