"""
Testes unitários da dependência de autorização `get_current_user`
(app/auth/dependencies.py) — a "porta" de todas as rotas protegidas.

A validação do JWT (`decodificar_token_acesso`) é uma dependência desta
função. Nos dois primeiros testes ela é trocada por um mock, para testar
apenas a decisão de `get_current_user`: liberar ou responder 401.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth import dependencies
from app.auth.dependencies import get_current_user
from app.auth.service import ALGORITHM, SECRET_KEY

ID_USUARIO = "0b0f7a52-6f0e-4c58-9d0c-2f3d6a7b8c9d"


def test_deve_liberar_acesso_e_devolver_o_id_quando_token_e_valido(monkeypatch):
    # Arrange
    decodificador = MagicMock(return_value=ID_USUARIO)
    monkeypatch.setattr(dependencies, "decodificar_token_acesso", decodificador)

    # Act
    id_usuario = get_current_user(token="token-valido")

    # Assert
    assert id_usuario == ID_USUARIO
    decodificador.assert_called_once_with("token-valido")


def test_deve_lancar_401_quando_token_e_invalido(monkeypatch):
    # Arrange — o decodificador avisa que o token não presta (devolve None)
    decodificador = MagicMock(return_value=None)
    monkeypatch.setattr(dependencies, "decodificar_token_acesso", decodificador)

    # Act
    with pytest.raises(HTTPException) as erro:
        get_current_user(token="token-adulterado")

    # Assert — tipo, status, mensagem e cabeçalho exigido pelo padrão Bearer
    assert erro.value.status_code == 401
    assert erro.value.detail == "Token inválido ou expirado"
    assert erro.value.headers == {"WWW-Authenticate": "Bearer"}


def test_deve_lancar_401_quando_token_expirou_ha_um_segundo():
    # Arrange — sem mock: token real, assinado com a chave certa, mas vencido
    token_vencido = jwt.encode(
        {"sub": ID_USUARIO, "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    # Act
    with pytest.raises(HTTPException) as erro:
        get_current_user(token=token_vencido)

    # Assert
    assert erro.value.status_code == 401
    assert erro.value.detail == "Token inválido ou expirado"
