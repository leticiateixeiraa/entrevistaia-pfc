import uuid

from pydantic import BaseModel


class StartInterviewIn(BaseModel):
    # Enquanto o módulo `questions` não existe, quem escolhe a categoria
    # é o próprio corpo da requisição em vez de vir de um catálogo real.
    category: str


class StartInterviewOut(BaseModel):
    session_id: uuid.UUID
    questions: list[str]


class AnswerIn(BaseModel):
    answer_text: str


class NextQuestionOut(BaseModel):
    session_id: uuid.UUID
    question: str | None
    order_index: int
    finished: bool

    # Indica se ESSA pergunta foi ajustada com base na resposta anterior —
    # é o que comprova o critério de aceitação da feature 3: "ao menos uma
    # pergunta subsequente é ajustada com base na resposta dada".
    adapted: bool
