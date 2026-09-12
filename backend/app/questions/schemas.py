import uuid

from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: str
    name: str
    description: str


class StartInterviewIn(BaseModel):
    job_title: str
    presentation_type: str
    job_description: str | None = None


class InterviewSessionOut(BaseModel):
    session_id: uuid.UUID
    questions: list[str]