import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.models.base import get_db
from app.questions import service
from app.questions.schemas import CategoryOut, InterviewSessionOut, StartInterviewIn


router = APIRouter(tags=["questions"])


@router.get("/questions/categories", response_model=list[CategoryOut])
def categories():
    return service.list_categories()


@router.post("/interviews", response_model=InterviewSessionOut, status_code=status.HTTP_201_CREATED)
def start_interview(
    payload: StartInterviewIn,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = (
        "apresentacao_academica"
        if payload.presentation_type == "apresentacao_academica"
        else "entrevista_de_emprego"
    )
    try:
        session = service.start_interview(db, uuid.UUID(user_id), category)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return InterviewSessionOut(session_id=session.id, questions=[session.current_question_text])