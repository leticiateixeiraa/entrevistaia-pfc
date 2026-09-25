import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

# feat(lgpd): versão vigente do Termo de Uso / Política de Privacidade.
# Ao publicar uma nova versão dos documentos, incremente este valor
# para que novos cadastros fiquem vinculados à versão correta.
CURRENT_TERMS_VERSION = "1.0"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None
    terms_accepted: bool
    terms_version: str = CURRENT_TERMS_VERSION

    @field_validator("terms_accepted")
    @classmethod
    def must_accept_terms(cls, value: bool) -> bool:
        if not value:
            raise ValueError(
                "É necessário aceitar o Termo de Uso e a Política de Privacidade para se cadastrar."
            )
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
