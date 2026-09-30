"""
feat(auth-backend): implementa endpoint POST /auth/register
feat(auth-backend): implementa endpoint POST /auth/login com JWT
feat(auth-backend): implementa endpoint GET /auth/me
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import UserCreate, UserLogin, UserOut, Token
from app.auth.service import hash_password, verify_password, create_access_token
from app.audit.service import record_event

router = APIRouter(prefix="/auth", tags=["auth"])

_DUMMY_HASH = hash_password("senha-inexistente-0")


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    email = str(user_in.email).strip().lower()
    existing = db.query(User).filter(func.lower(User.email) == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    user = User(
        email=email,
        hashed_password=hash_password(user_in.password),
        name=user_in.name,
        # feat(lgpd): consentimento é pré-requisito para o cadastro
        # (validado em UserCreate.must_accept_terms).
        terms_accepted_at=datetime.now(timezone.utc),
        terms_version=user_in.terms_version,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_event(db, "auth.registered", user.id, "user", str(user.id), ip_address=_client_ip(request))
    record_event(
        db,
        "lgpd.consent_accepted",
        user.id,
        "user",
        str(user.id),
        {"terms_version": user_in.terms_version},
    )
    db.commit()
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    email = str(credentials.email).strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    password_ok = verify_password(
        credentials.password, user.hashed_password if user else _DUMMY_HASH
    )
    if not user or not password_ok:
        # A falha também é auditada (sem guardar a senha nem o e-mail digitado).
        record_event(
            db,
            "auth.login_failed",
            user.id if user else None,
            "user",
            str(user.id) if user else None,
            ip_address=_client_ip(request),
        )
        db.commit()
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    access_token = create_access_token(user_id=str(user.id))
    record_event(db, "auth.login", user.id, "user", str(user.id), ip_address=_client_ip(request))
    db.commit()
    return Token(access_token=access_token)

@router.get("/me", response_model=UserOut)
def me(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user
