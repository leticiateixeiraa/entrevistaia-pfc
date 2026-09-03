"""
chore(auth): configura middleware de autenticação nas rotas protegidas

Dependency reutilizável por Leonardo e Gabriel nos próprios endpoints:

    from app.auth.dependencies import get_current_user

    @router.get("/rota-protegida")
    def minha_rota(user_id: str = Depends(get_current_user)):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.service import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
