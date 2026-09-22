"""
feat(auth-backend): implementa endpoint POST /auth/register
feat(auth-backend): implementa endpoint POST /auth/login com JWT
feat(auth-backend): implementa endpoint GET /auth/me
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import UserCreate, UserLogin, UserOut, Token
from app.auth.service import hash_password, verify_password, create_access_token
from app.audit.service import record_event

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    email = str(user_in.email).strip().lower()
    existing = db.query(User).filter(func.lower(User.email) == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    user = User(
        email=email,
        hashed_password=hash_password(user_in.password),
        name=user_in.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_event(db, "auth.registered", user.id, "user", str(user.id))
    db.commit()
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    email = str(credentials.email).strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    access_token = create_access_token(user_id=str(user.id))
    record_event(db, "auth.login", user.id, "user", str(user.id))
    db.commit()
    return Token(access_token=access_token)

@router.get("/me", response_model=UserOut)
def me(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user
